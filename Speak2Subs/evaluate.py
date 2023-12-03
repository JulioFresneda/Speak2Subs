import os.path
import json
import jiwer
from Speak2Subs import subtitle


# https://github.com/jitsi/jiwer
class Evaluator:
    def __init__(self, vtt_folder):
        self.vtt_folder_path = os.path.abspath(vtt_folder)

        self.media_metrics = {}
        self.detect_vtt_files()

        self.dataset_name = os.path.basename(vtt_folder)

        for mm in self.media_metrics.values():
            for asr in self.asr_names:
                mm.compliance = evaluate_compliance(mm.ref_vtt, mm.pred_vtt[asr])
        une_compliance = evaluate_compliance()
        # self._load_exec_time()

    def _load_exec_time(self):
        with open(os.path.join(self.vtt_folder_path, "execution_times_" + self.dataset_name + ".json"),
                  'r') as json_file:
            loaded_data = json.load(json_file)
        self.execution_time = loaded_data['execution_time']

    def detect_vtt_files(self):

        self.media_names = []
        self.asr_names = []

        for mf in [os.path.join(self.vtt_folder_path, file) for file in os.listdir(self.vtt_folder_path) if
                   file.endswith(".vtt")]:
            media_name = os.path.basename(mf).replace(".vtt", "")
            self.media_names.append(media_name)

            asr_files = {}
            for asrf in [os.path.join(self.vtt_folder_path, folder) for folder in os.listdir(self.vtt_folder_path) if
                         folder.endswith("_VTT")]:
                asr_name = os.path.basename(asrf).replace("_VTT", "")
                if (asr_name not in self.asr_names):
                    self.asr_names.append(asr_name)
                files = [os.path.join(asrf, file) for file in os.listdir(asrf) if file.endswith("_PRED_.vtt")]
                for f in files:
                    tmp = os.path.basename(f).replace("_PRED_.vtt", "")
                    if (tmp == media_name):
                        asr_files[asr_name] = f

            self.media_metrics[media_name] = MediaMetrics(media_name, mf, asr_files)


class MediaMetrics:
    def __init__(self, name, ref_vtt_path: str, pred_vtt_dict_paths: dict):
        self.ref_vtt = ref_vtt_path
        self.pred_vtt = pred_vtt_dict_paths
        self.name = name

        self.metrics = {}
        self.compliance_metrics = {}

        for asr in self.pred_vtt.keys():
            metrics = evaluate_classics(self.ref_vtt, self.pred_vtt[asr])
            self.metrics[asr] = metrics

            self.compliance_metrics[asr] = evaluate_compliance(self.pred_vtt[asr])
        self.compliance_metrics['reference'] = evaluate_compliance(self.ref_vtt)




def evaluate_classics(reference, predicted):
    _, reference = subtitle.load_template(reference)
    _, predicted = subtitle.load_template(predicted)

    output = jiwer.process_words(reference, predicted)
    print(jiwer.visualize_alignment(output))
    return {'wer': output.wer, 'mer': output.mer, 'wil': output.wil, 'wip': output.wip}


def evaluate_compliance(vtt_path):
    # Reglas
    vtt_ts, vtt = subtitle.load_template(vtt_path)

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


    eval = {"4_3":comply_4_3, "4_6":comply_4_6, "5_1":comply_5_1, "total":len(vtt)}
    print(eval)
    return eval



# No more than 3 lines
def eval_une_4_3(sentence):
    return sentence.count('\n') <= 2

# No more than 37 char per line
def eval_une_4_6(sentence):
    comply_bool = True
    for sub_s in sentence.split('\n'):
        if len(sub_s) > 37:
            comply_bool = False
    return comply_bool

# No more than 15 char/s
def eval_une_5_1(sentence, duration):
    sen_len = len(sentence)
    sen_sec = duration
    vel = sen_len / sen_sec
    duration_comply = sen_len / 15
    return vel <= 15, duration_comply


#evaluator = Evaluator("../datasets/mda")
evaluate_compliance("/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/mda_1.vtt")