from enum import Enum
import os  # Importing the os module for operating system-related functionality
import shutil

from .container_manager import ContainerManager
import vad
import media_dataset

class ASRNames(Enum):
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    SPEECHBRAIN = 'speechbrain'
    TORCH = 'torch'
    WHISPER = 'whisper'






class Revolver:
    def __init__(self, ASR, dataset, config):
        if isinstance(ASR, str) and ASR == 'all':
            self.asr_to_apply = list(ASRNames)
        elif isinstance(ASR, list) and all(item.lower() in ASRNames for item in ASR):
            self.asr_to_apply = ASR.copy()
        elif isinstance(ASR, ASRNames):
            self.asr_to_apply = [ASR]


        self.conf = config

        self.host_volume_path = os.path.join(os.path.dirname(dataset.parent_path), 'host_volume')
        if not os.path.exists(self.host_volume_path):
            os.mkdir(self.host_volume_path)

        self.container_manager = ContainerManager(self.asr_to_apply, self.host_volume_path, self.conf['image_names'])



    def shot(self, dataset):
        for asr in self.asr_to_apply:
            for media in dataset.media:
                self._copy_media_to_container_volume(media, self.host_volume_path)
                self.container_manager.execute_in_container(asr)



    def _copy_media_to_container_volume(self, media, host_volume_path):

        host_media_path = os.path.join(host_volume_path, 'media')
        if not os.path.exists(host_media_path):
            os.makedirs(host_media_path)
        files = os.listdir(host_media_path)

        # Iterate through the files and remove each one
        for file_name in files:
            file_path = os.path.join(host_media_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        for file in media.vad_segments_paths:
            dest_file = os.path.join(host_media_path, os.path.basename(file))
            shutil.copy2(file, dest_file)










def transcript(dataset, config, ASR='all', VAD=True, max_speech_duration=float('inf'), split=False):

    rev = Revolver(ASR, dataset, config)
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
        rev.shot(ds)





