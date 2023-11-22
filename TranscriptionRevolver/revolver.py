from enum import Enum
import subprocess  # Importing the subprocess module to execute shell commands
import os  # Importing the os module for operating system-related functionality
import docker
import json
import ast
import shutil

from .container_manager import ContainerManager

class ASRNames(Enum):
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    SPEECHBRAIN = 'speechbrain'
    TORCH = 'torch'
    WHISPER = 'whisper'

class Revolver:
    def __init__(self, ASR, dataset):
        if isinstance(ASR, str) and ASR == 'all':
            self.asr_to_apply = list(ASRNames)
        elif isinstance(ASR, list) and all(item.lower() in ASRNames for item in ASR):
            self.asr_to_apply = ASR.copy()
        elif isinstance(ASR, ASRNames):
            self.asr_to_apply = [ASR]

        self.host_volume_path = os.path.join(os.path.dirname(dataset.parent_path), 'host_volume')
        if not os.path.exists(self.host_volume_path):
            os.mkdir(self.host_volume_path)

        self.container_manager = ContainerManager(self.asr_to_apply, self.host_volume_path)



    def shot(self, dataset):
        for asr in self.asr_to_apply:
            for media in dataset.media:
                self._copy_media_to_container_volume(media, self.host_volume_path)
                self.container_manager.execute_in_container(asr)



    def _copy_media_to_container_volume(self, media, host_volume_path):
        files = os.listdir(host_volume_path)

        # Iterate through the files and remove each one
        for file_name in files:
            file_path = os.path.join(host_volume_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        for file in media.vad_segments_paths:
            dest_file = os.path.join(host_volume_path, os.path.basename(file))
            shutil.copy2(file, dest_file)

















