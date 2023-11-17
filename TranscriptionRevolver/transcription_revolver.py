from .Datasets import dataset_loader
from .ASR import revolver
from .VAD import vad

def transcript(dataset, ASR='all', VAD=True):

    rev = revolver.Revolver(ASR)

    if isinstance(dataset, dataset_loader.Dataset):
        if (VAD):
            for vid in dataset.getVideos():
                vad.apply_vad(vid)

    elif isinstance(dataset, list) and all(isinstance(item, dataset_loader.Dataset) for item in dataset):
        pass

    elif isinstance(dataset, tuple) and len(dataset) == 2 and all(isinstance(item, str) for item in dataset):
        pass

    else:
        # Handle unsupported input or raise an error
        raise ValueError("Unsupported input type")


