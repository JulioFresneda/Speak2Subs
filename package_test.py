from TranscriptionRevolver.Datasets import media_dataset
from TranscriptionRevolver import transcription_revolver
from TranscriptionRevolver import revolver
import json

dsloader = media_dataset.DatasetLoader('./datasets')

mda_ds = dsloader.get('mda')
random = dsloader.getRandom()
all = dsloader.getAll()

print(random)

with open('./configuration.json', 'r') as file:
    config = json.load(file)

transcription_revolver.transcript(random, config, ASR=revolver.ASRNames.WHISPER, VAD=True, split=True, max_speech_duration=30)
  # Use the appropriate encoding