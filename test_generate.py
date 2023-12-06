from Speak2Subs import media
from Speak2Subs import speak2subs
import json

asr_list = list(speak2subs.ASR)
print(asr_list)


speak2subs.transcript('./datasets/mda',
                      export_path = './results',
                      asr='all',
                      use_vad=False,
                      segment=True,
                      sentences=False,
                      max_speech_duration=30,
                      use_vtt_template=True,
                      reduce_noise=False)

