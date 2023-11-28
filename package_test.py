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


speak2subs.transcript(dataset, asr=speak2subs.ASRNames.VOSK, use_vad=True, segment=True, max_speech_duration=30, eval_mode=True)
