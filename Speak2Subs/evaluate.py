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
        #self._load_exec_time()


    def _load_exec_time(self):
        with open(os.path.join(self.vtt_folder_path, "execution_times_" + self.dataset_name + ".json"), 'r') as json_file:
            loaded_data = json.load(json_file)
        self.execution_time = loaded_data['execution_time']

    def detect_vtt_files(self):

        self.media_names = []
        self.asr_names = []

        for mf in [os.path.join(self.vtt_folder_path, file) for file in os.listdir(self.vtt_folder_path) if file.endswith(".vtt")]:
            media_name = os.path.basename(mf).replace(".vtt","")
            self.media_names.append(media_name)

            asr_files = {}
            for asrf in [os.path.join(self.vtt_folder_path, folder) for folder in os.listdir(self.vtt_folder_path) if folder.endswith("_VTT")]:
                asr_name = os.path.basename(asrf).replace("_VTT", "")
                if(asr_name not in self.asr_names):
                    self.asr_names.append(asr_name)
                files = [os.path.join(asrf, file) for file in os.listdir(asrf) if file.endswith("_PRED_.vtt")]
                for f in files:
                    tmp = os.path.basename(f).replace("_PRED_.vtt","")
                    if(tmp == media_name):
                        asr_files[asr_name] = f

            self.media_metrics[media_name] = MediaMetrics(media_name, mf, asr_files)



class MediaMetrics:
    def __init__(self, name, ref_vtt_path: str, pred_vtt_dict_paths: dict):
        self.ref_vtt = ref_vtt_path
        self.pred_vtt = pred_vtt_dict_paths
        self.name = name

        self.metrics = {}
        for asr in self.pred_vtt.keys():
            metrics = evaluate_wer(self.ref_vtt, self.pred_vtt[asr])
            self.metrics[asr] = metrics


class ComplianceMediaMetrics:
    def __init__(self, id=None, comply, total):
        self.id = id
        self.comply = comply
        self.total = total






def evaluate_wer(reference, predicted):
    _, reference = subtitle.load_template(reference)
    _, predicted = subtitle.load_template(predicted)

    output = jiwer.process_words(reference, predicted)
    print(jiwer.visualize_alignment(output))
    return {'wer': output.wer, 'mer': output.mer, 'wil': output.wil, 'wip': output.wip}

def evaluate_compliance(reference, predicted, manual_evaluation = False):
    # Reglas
    reference_ts, reference = subtitle.load_template(reference)
    predicted_ts, predicted = subtitle.load_template(predicted)

    # 4.6 - Maximo de caracteres por linea - 37
    ref_eval_4_6 = _eval_une_4_6(reference)
    pred_eval_4_6 = _eval_une_4_6(predicted)


    # 5.1 - 15 caracteres por segundo max
    ref_eval_4_6 = _eval_une_5_3(reference_ts)
    pred_eval_4_6 = _eval_une_5_3(predicted_ts)

    # 5.1 - 15 caracteres por segundo max
    ref_eval_4_6 = _eval_une_5_3(reference_ts)
    pred_eval_4_6 = _eval_une_5_3(predicted_ts)




def _eval_une_4_6(sentences):
    comply = 0
    for s in sentences:
        if(len(s) <= 37):
            comply+=1
    total = len(sentences)
    return {'comply':comply, 'total':total}

def _eval_une_5_3(sentences_ts):
    comply = 0
    for s in sentences_ts:
        sen_len = len(s['text'])
        sen_sec = s['end'] - s['start']
        vel = sen_len/sen_sec
        if vel<=15
            comply+=1
    total = len(sentences_ts)
    return {'comply':comply, 'total':total}

#evaluator = Evaluator("../datasets/mda")
