from Speak2Subs import transcription_revolver, media_dataset
from Speak2Subs import revolver
import json

dsloader = media_dataset.DatasetLoader('./datasets')

mda_ds = dsloader.get('mda')
random = dsloader.getRandom()
all = dsloader.getAll()

print(random)

with open('./configuration.json', 'r') as file:
    config = json.load(file)


# VOSK - OK
# NEMO - OK
# WHISPER - OK
# SPEECHBRAIN - OK
# WHISPERX - OK
# TORCH - TODO




transcription_revolver.transcript(random, config, ASR=revolver.ASRNames.WHISPERX, VAD=True, split=True, max_speech_duration=30)
  # Use the appropriate encoding


