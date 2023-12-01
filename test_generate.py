from Speak2Subs import media
from Speak2Subs import speak2subs
import json

asr_list = list(speak2subs.ASR)
print(asr_list)


speak2subs.transcript('./datasets/mda', asr=['whisper','vosk'], use_vad=True, segment=True, sentences=False, max_speech_duration=30, use_vtt_template=True)



ref = "/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/mda_1.vtt"
pred = "/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/whisper_VTT/mda_1_PRED_.vtt"

speak2subs.eval(ref, pred)