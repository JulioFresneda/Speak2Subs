from Speak2Subs import speak2subs

#original = speak2subs.evaluateCompliance("./datasets/mda/mda_1.vtt")
generated = speak2subs.evaluateCompliance("./results/whisperx_VTT/mda_1_PRED_.vtt")


   #                                 , "./results/whisper_VTT/mda_1_PRED_.vtt")
print(generated)

result = speak2subs.evaluatePair("./datasets/mda/mda_1.vtt", "./results/whisperx_VTT/mda_1_PRED_.vtt")
print(result)

