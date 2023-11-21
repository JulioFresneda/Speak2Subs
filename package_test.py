from TranscriptionRevolver.Datasets import media_dataset
from TranscriptionRevolver import transcription_revolver
from TranscriptionRevolver import revolver

dsloader = media_dataset.DatasetLoader('./datasets')

mda_ds = dsloader.get('mda')
random = dsloader.getRandom()
all = dsloader.getAll()

print(random)

transcription_revolver.transcript(random, ASR=revolver.ASRNames.VOSK, VAD=True, split=True, max_speech_duration=30)
