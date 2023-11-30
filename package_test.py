from Speak2Subs import media
from Speak2Subs import speak2subs
import json

dataset = media.Dataset('./datasets/mda')


# VOSK - OK
# NEMO - OK
# WHISPER - OK
# SPEECHBRAIN - OK
# WHISPERX - OK
# TORCH - TODO
# SEAMLESS - OK


#vtt_files = speak2subs.transcript(dataset, asr=speak2subs.ASRNames.SEAMLESS, use_vad=True, segment=True, sentences=True, max_speech_duration=10, eval_mode=True)

# Test
ref_vtt = "/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/mda_1.vtt"
pred_vtt = "/home/juliofgx/PycharmProjects/Speak2Subs/datasets/mda/mda_1_PRED_.vtt"
speak2subs.evaluate(ref_vtt, pred_vtt)
