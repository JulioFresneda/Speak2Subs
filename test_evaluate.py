from Speak2Subs import speak2subs

speak2subs.evaluateFolder( "./datasets/mda", "./results", "mda")

result = speak2subs.evaluatePair("./datasets/mda/mda_3.vtt", "./results/whisperx_VTT/mda_3_PRED_.vtt")

