import wave
import sys
import os
import json

from vosk import Model, KaldiRecognizer, SetLogLevel

import logging


def save_progress(string):
    with open('/volume/progress.txt', 'w') as file:
        # Write a string to the file
        file.write(string)
        file.close()


# Disable all logging from Vosk
logging.getLogger('vosk').setLevel(logging.ERROR)

# print("Hello from the vosk asr image")

# You can set log level to -1 to disable debug messages
SetLogLevel(-1)

media_volume = "/volume/media"

complete_result = {}

for i, media in enumerate(sorted(os.listdir(media_volume)), start=1):
    print(media)
    wf = wave.open(os.path.join(media_volume, media), "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    model = Model(lang="es")

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    # rec.SetPartialWords(True)

    # Read the entire audio file
    audio_data = wf.readframes(wf.getnframes())

    # Feed the entire audio data to the recognizer
    rec.AcceptWaveform(audio_data)

    # Get the final recognized result
    final_result = rec.FinalResult()
    final_result = json.loads(final_result)
    try:
        final_result['words_ts'] = final_result.pop('result')
    except:
        final_result['words_ts'] = []
    for word in final_result['words_ts']:
        word['score'] = word.pop('conf')
        word['token'] = word.pop('word')
    complete_result[media] = final_result
    save_progress(str(i) + '/' + str(len(os.listdir(media_volume))))

# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()

save_progress("DONE")
