from Speak2Subs import media
from Speak2Subs import speak2subs
import json

asr_list = list(speak2subs.ASR)
print(asr_list)


speak2subs.transcript('./datasets/mda',
                      export_path = './results',
                      asr=['vosk', 'whisper', 'whisperx'],
                      use_vad=True,
                      segment=True,
                      sentences=False,
                      max_speech_duration=30,
                      use_vtt_template=True,
                      reduce_noise=False)



#ref = "/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/mda_1.vtt"
#pred = "/home/juliofgx/PycharmProjects/Speak2Subs/results/vosk_VTT/mda_1_PRED_.vtt"

#speak2subs.eval(ref, pred)