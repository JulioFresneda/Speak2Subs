from .Datasets import media_dataset
from . import revolver
from .VAD import vad

def transcript(dataset, ASR='all', VAD=True, max_speech_duration=float('inf'), split=False):

    rev = revolver.Revolver(ASR)
    to_transcript = []

    if isinstance(dataset, media_dataset.Dataset):
        to_transcript.append(dataset)

    elif isinstance(dataset, list) and all(isinstance(item, media_dataset.Dataset) for item in dataset):
        to_transcript = dataset

    elif isinstance(dataset, tuple) and len(dataset) == 2 and all(isinstance(item, str) for item in dataset):
        pass

    else:
        # Handle unsupported input or raise an error
        raise ValueError("Unsupported input type")

    if (VAD):
        for ds in to_transcript:
            for m in ds.media:
                vad.apply_vad(m, max_speech_duration, split=split)
                pass


    for ds in to_transcript:
        rev.apply_asr(ds, original=False, vad=False, vad_segments=True)



