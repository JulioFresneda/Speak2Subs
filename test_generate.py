from Speak2Subs import speak2subs
import os

# = ["mda", "mat", "cdp", "atc", "ddl"]
#for ds in datasets:
speak2subs.transcript('./datasets/mda/audios/Demo.mp4',
                      export_path='./results',
                      asr='whisperx',
                      use_vad=True,
                      segment=True,
                      group_segments=True,
                      max_speech_duration=30,
                      use_vtt_template=False,
                      reduce_noise=False)



