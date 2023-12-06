from Speak2Subs import media
from Speak2Subs import speak2subs
import json

# Test
speak2subs.vtt_evaluator.evaluate_error_metrics("/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/mda_7.vtt", "/home/juliofgx/PycharmProjects/Speak2Subs/results/whisper_VTT/mda_7_PRED_.vtt")
speak2subs.evaluate("mda", "./datasets/mda", "./results")
