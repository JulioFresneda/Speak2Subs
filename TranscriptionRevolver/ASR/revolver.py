from enum import Enum
from TranscriptionRevolver.ASR import nemo_asr
class ASRNames(Enum):
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    SPEECHBRAIN = 'speechbrain'
    TORCH = 'torch'
    WHISPER = 'whisper'

class Revolver:
    def __init__(self, ASR):
        if isinstance(ASR, str) and ASR == 'all':
            self.asr_to_apply = list(ASRNames)
        elif isinstance(ASR, list) and all(item.lower() in ASRNames for item in ASR):
            self.asr_to_apply = ASR.copy()


    def apply_asr(self, dataset, original, vad, vad_segments):
        for asr in self.asr_to_apply:
            if(original):
                for media in dataset.media:
                    self.shot(asr, media.original_media_path)
            elif(vad):
                for media in dataset.media:
                    self.shot(asr, media.vad_media_path)
            elif(vad_segments):
                for media in dataset.media:
                    for segment in media.vad_segments_paths:
                        self.shot(asr, segment)




    def shot(self, asr, media_path):
        if(asr == ASRNames.NEMO):
            text, timestamps = nemo_asr.apply_nemo(media_path)
            print(text)
            pass












