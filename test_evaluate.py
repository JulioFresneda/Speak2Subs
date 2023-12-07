from Speak2Subs import media
from Speak2Subs import speak2subs
import json

# Test
#speak2subs.vtt_evaluator.evaluate_error_metrics("/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/mda_7.vtt", "/home/juliofgx/PycharmProjects/Speak2Subs/results/whisper_VTT/mda_7_PRED_.vtt")
speak2subs.evaluateFolder( "./datasets/mda", "./results", "mda")
res = speak2subs.evaluatePair("./datasets/mda/mda_3.vtt", "./results/whisperx_VTT/mda_3_PRED_.vtt")
print(res)