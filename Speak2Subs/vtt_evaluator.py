import os.path
import json
import jiwer
from Speak2Subs.vtt_loader import load_vtt_template
import pandas as pd


# https://github.com/jitsi/jiwer
class Evaluator:
    def __init__(self, dataset_name, vtt_reference_folder, results_folder):
        self.media_metrics = {}
        self.asr_names = []
        self.media_names = []
        self.vtt_reference_folder_path = os.path.abspath(vtt_reference_folder)
        self.results_folder = results_folder
        self.dataset_name = dataset_name

        self.detect_vtt_files()
        self._generate_metrics()
        self._export_to_excel()

    def _export_to_excel(self):
        export_path = os.path.join(self.results_folder, "metrics.xlsx")
        if not os.path.exists(export_path):
            self.metrics_df.to_excel(export_path, index=False)
        else:
            # Read existing Excel file
            existing_df = pd.read_excel(export_path)

            # Concatenate DataFrames vertically
            combined_df = pd.concat([existing_df, self.metrics_df], ignore_index=True)

            # Save the combined DataFrame back to Excel
            combined_df.to_excel(export_path, index=False)

    def _generate_metrics(self):
        self.metrics_df_list = []
        for media_name in self.media_names:
            mf = self.media_files[media_name]
            all_asr_mm = self.load_metrics(self.results_folder, mf, self.asr_files[media_name], self.dataset_name)
            for asr_name in self.asr_names:
                error_m = all_asr_mm['error_metrics'][asr_name]
                comp_m = all_asr_mm['compliance_metrics'][asr_name]
                if asr_name in all_asr_mm['execution_metrics']['execution_time'][media_name + ".wav"].keys():
                    exec_m = all_asr_mm['execution_metrics']['execution_time'][media_name + ".wav"][asr_name]
                else:
                    exec_m = 0

                self.metrics_df_list.append(
                    MediaMetrics(self.dataset_name, media_name, asr_name, error_m, comp_m, exec_m))
                self.metrics_df = MediaMetrics.vstack_metrics(self.metrics_df_list)

    def _load_exec_time(self):
        with open(os.path.join(self.vtt_folder_path, "execution_times_" + self.dataset_name + ".json"),
                  'r') as json_file:
            loaded_data = json.load(json_file)
        self.execution_time = loaded_data['execution_time']

    def detect_vtt_files(self):

        self.media_names = []
        self.media_files = {}
        self.asr_names = []
        self.asr_files = {}

        for mf in [os.path.join(self.vtt_reference_folder_path, file) for file in
                   os.listdir(self.vtt_reference_folder_path) if
                   file.endswith(".vtt")]:
            media_name = os.path.basename(mf).replace(".vtt", "")
            self.media_files[media_name] = mf
            self.media_names.append(media_name)

            asr_files = {}
            for asrf in [os.path.join(self.results_folder, folder) for folder in os.listdir(self.results_folder) if
                         folder.endswith("_VTT")]:
                asr_name = os.path.basename(asrf).replace("_VTT", "")

                if asr_name not in self.asr_names:
                    self.asr_names.append(asr_name)
                files = [os.path.join(asrf, file) for file in os.listdir(asrf) if file.endswith("_PRED_.vtt")]
                for f in files:
                    tmp = os.path.basename(f).replace("_PRED_.vtt", "")
                    if tmp == media_name:
                        asr_files[asr_name] = os.path.abspath(f)

            self.asr_files[media_name] = asr_files

    def load_metrics(self, results_folder, media_file, asr_files, dataset_name):

        error_metrics = {}
        compliance_metrics = {}

        for asr in asr_files.keys():
            error_metrics[asr] = evaluate_error_metrics(media_file, asr_files[asr])

            compliance_metrics[asr] = evaluate_compliance(asr_files[asr])
        compliance_metrics['reference'] = evaluate_compliance(media_file)

        execution_metrics = load_execution_times(results_folder, dataset_name)

        return {'error_metrics': error_metrics, 'compliance_metrics': compliance_metrics,
                'execution_metrics': execution_metrics}


class MediaMetrics:
    def __init__(self, dataset_name, media_name, asr_name, error_metrics, compliance_metrics, execution_metrics):
        self.media_name = media_name
        self.asr_name = asr_name
        self.metrics = {'dataset': dataset_name, 'media': media_name, 'ASR': asr_name}
        self._load_error_metrics(error_metrics)
        self._load_execution_metrics(execution_metrics)
        self._load_compliance_metrics(compliance_metrics)

        self.metrics_df = pd.DataFrame.from_dict(self.metrics)

    @staticmethod
    def vstack_metrics(metrics: list):
        mlist = []
        for m in metrics:
            mlist.append(m.metrics_df)
        return pd.concat(mlist, axis=0, ignore_index=True)

    def _load_execution_metrics(self, execution_metrics):
        self.metrics['exec_time'] = [execution_metrics]

    def _load_compliance_metrics(self, compliance_metrics):
        self.metrics['une_4_3'] = [compliance_metrics['4_3']]
        self.metrics['une_4_6'] = [compliance_metrics['4_6']]
        self.metrics['une_5_1'] = [compliance_metrics['5_1']]
        self.metrics['une_total'] = [compliance_metrics['total']]

    def _load_error_metrics(self, error_metrics):
        # Not normalized
        self.metrics['wer'] = [error_metrics['not_normalized']['wer']]
        self.metrics['mer'] = [error_metrics['not_normalized']['mer']]
        self.metrics['wil'] = [error_metrics['not_normalized']['wil']]
        self.metrics['wip'] = [error_metrics['not_normalized']['wip']]
        self.metrics['wwer'] = [error_metrics['not_normalized']['wwer']]
        self.metrics['wmer'] = [error_metrics['not_normalized']['wmer']]

        # Normalized
        self.metrics['nwer'] = [error_metrics['normalized']['nwer']]
        self.metrics['nmer'] = [error_metrics['normalized']['nmer']]
        self.metrics['nwil'] = [error_metrics['normalized']['nwil']]
        self.metrics['nwip'] = [error_metrics['normalized']['nwip']]
        self.metrics['nwwer'] = [error_metrics['normalized']['nwwer']]
        self.metrics['nwmer'] = [error_metrics['normalized']['nwmer']]

        # Mislocations
        self.metrics['mislocation_rate'] = [error_metrics['mislocated']['mislocated_rate']]
        self.metrics['mislocations'] = [error_metrics['mislocated']['mislocated']]
        self.metrics['mislocations_and_not'] = [error_metrics['mislocated']['total']]

        # NER
        self.metrics['ner'] = [error_metrics['ner']['ner']]
        self.metrics['ner_N'] = [error_metrics['ner']['N']]
        self.metrics['ner_E'] = [error_metrics['ner']['E']]
        self.metrics['ner_R'] = [error_metrics['ner']['R']]


def load_execution_times(folder, dataset_name):
    filepath = os.path.join(folder, "execution_times_" + dataset_name + ".json")
    with open(filepath, 'r') as json_file:
        # Load the JSON content
        return json.load(json_file)


def evaluate_error_metrics(reference, predicted):
    _, reference = load_vtt_template(reference)
    _, predicted = load_vtt_template(predicted)

    not_normalized = not_normalized_error_metrics(reference, predicted)
    normalized, ref_norm, pred_norm = normalized_error_metrics(reference, predicted)
    mislocated = evaluate_mislocated_words(ref_norm, pred_norm)
    ner = evaluate_ner(reference, predicted)

    return {'not_normalized': not_normalized, 'normalized': normalized, 'mislocated': mislocated, 'ner': ner}


def not_normalized_error_metrics(reference, predicted):
    try:
        output = jiwer.process_words(reference, predicted)
        print(jiwer.visualize_alignment(output))
    except:
        print(3)
    wwer, wmer = _wwer_wmer(output.substitutions, output.deletions, output.insertions, output.hits)
    not_normalized = {'wer': output.wer, 'mer': output.mer, 'wil': output.wil, 'wip': output.wip, 'wwer': wwer,
                      'wmer': wmer}
    return not_normalized


def normalized_error_metrics(reference, predicted):
    ref_norm = []
    pred_norm = []
    for r, p in zip(reference, predicted):
        ref_norm.append(r.lower())
        pred_norm.append(p.lower())

    output = jiwer.process_words(jiwer.RemovePunctuation()(ref_norm), jiwer.RemovePunctuation()(pred_norm))
    wwer, wmer = _wwer_wmer(output.substitutions, output.deletions, output.insertions, output.hits)
    normalized = {'nwer': output.wer, 'nmer': output.mer, 'nwil': output.wil, 'nwip': output.wip, 'nwwer': wwer,
                  'nwmer': wmer}
    return normalized, ref_norm, pred_norm


def _wwer_wmer(num_substitutions, num_deletions, num_insertions, num_hits):
    S, D, I, H = num_substitutions, num_deletions, num_insertions, num_hits

    wwer = float(S + 0.5 * D + 0.5 * I) / float(S + D + H)
    wmer = float(S + 0.5 * D + 0.5 * I) / float(H + S + D + I)

    return wwer, wmer


def evaluate_compliance(vtt_path):
    # Reglas
    vtt_ts, vtt = load_vtt_template(vtt_path, strip_newlines=False)

    comply_4_3 = 0
    comply_4_6 = 0
    comply_5_1 = 0

    for sentence_ts, sentence in zip(vtt_ts, vtt):
        if eval_une_4_3(sentence):
            comply_4_3 += 1
        if eval_une_4_6(sentence):
            comply_4_6 += 1
        if eval_une_5_1(sentence, sentence_ts['end'] - sentence_ts['start'])[0]:
            comply_5_1 += 1

    eval = {"4_3": comply_4_3 / len(vtt), "4_6": comply_4_6 / len(vtt), "5_1": comply_5_1 / len(vtt), "total": len(vtt)}
    print(eval)
    return eval


def evaluate_ner(reference, prediction):
    total = 0
    edition = 0
    recognition = 0

    for ref, pred in zip(reference, prediction):
        for pred_tkn in pred.split(" "):
            if pred_tkn not in ref and _normalize_string(pred_tkn) in _normalize_string(ref):
                edition += 1
            elif pred_tkn not in ref and _normalize_string(pred_tkn) not in _normalize_string(ref):
                recognition += 1
            total += 1

    ner = (total - edition - recognition) / total
    ner_dict = {'ner': ner, 'N': total, "E": edition, "R": recognition}
    return ner_dict


def evaluate_mislocated_words(reference, prediction):
    mislocated = 0
    total = len(reference)

    for i in range(1, total - 1):
        last_word_ref = _normalize_string(reference[i - 1].split(" ")[-1])
        current_word_pred = _normalize_string(prediction[i].split(" ")[0])
        if last_word_ref == current_word_pred:
            mislocated += 1

        last_word_pred = _normalize_string(prediction[i - 1].split(" ")[-1])
        current_word_ref = _normalize_string(reference[i].split(" ")[0])
        if last_word_pred == current_word_ref:
            mislocated += 1

    return {'mislocated_rate': mislocated / total, 'mislocated': mislocated, 'total': total}


def _normalize_string(string):
    return string.lower().replace(".", "").replace(",", "").replace(";", "").replace(":", "").replace("?", "")


# No more than 3 lines
def eval_une_4_3(sentence):
    last_newline_index = sentence.rfind('\n')
    finalnewline = 0
    if last_newline_index != -1 and last_newline_index == len(sentence) - 1:
        finalnewline = 1
    return sentence.count('\n') - finalnewline < 2


# No more than 37 char per line
def eval_une_4_6(sentence):
    comply_bool = True
    for sub_s in sentence.split('\n'):
        sub_wo_spaces = sub_s

        while len(sub_wo_spaces) > 0 and sub_wo_spaces[0] == ' ':
            sub_wo_spaces = sub_wo_spaces[1:]
        while len(sub_wo_spaces) > 0 and sub_wo_spaces[-1] == ' ':
            sub_wo_spaces = sub_wo_spaces[:-1]
        if len(sub_wo_spaces) > 37:
            comply_bool = False
    return comply_bool


# No more than 15 char/s
def eval_une_5_1(sentence, duration):
    sen_len = len(sentence)
    sen_sec = duration
    if sen_sec != 0:
        vel = sen_len / sen_sec
    else:
        vel = 0
    duration_comply = sen_len / 15
    return vel <= 15, duration_comply


if __name__ == "__main__":
    evaluator = Evaluator("mda", "../datasets/mda", "../results")
