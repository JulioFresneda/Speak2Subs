from TranscriptionRevolver.Datasets import dataset_loader
from TranscriptionRevolver.ASR import revolver
from TranscriptionRevolver import transcription_revolver

dsloader = dataset_loader.DatasetLoader('./datasets')

mda_ds = dsloader.get('mda')
random = dsloader.getRandom()
all = dsloader.getAll()

print(random)

transcription_revolver.transcript(random, VAD=True, split=True, max_speech_duration=30)
