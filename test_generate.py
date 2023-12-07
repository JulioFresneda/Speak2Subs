from Speak2Subs import speak2subs

speak2subs.transcript('./datasets/mda/mda_3.mp4',
                      export_path='./results',
                      asr='all',
                      use_vad=True,
                      segment=True,
                      group_segments=True,
                      max_speech_duration=30,
                      use_vtt_template=True,
                      reduce_noise=False)


