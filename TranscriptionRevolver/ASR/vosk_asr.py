import wave
import sys
import os
import json

from vosk import Model, KaldiRecognizer, SetLogLevel

#print("Hello from the vosk ASR image")

# You can set log level to -1 to disable debug messages
SetLogLevel(-1)

media_volume = "/media"

complete_result = []
for media in os.listdir(media_volume):

    wf = wave.open(os.path.join(media_volume,media), "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    model = Model(lang="es")



    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    #rec.SetPartialWords(True)



    # Read the entire audio file
    audio_data = wf.readframes(wf.getnframes())

    # Feed the entire audio data to the recognizer
    rec.AcceptWaveform(audio_data)

    # Get the final recognized result
    final_result = rec.FinalResult()
    final_result = json.loads(final_result)
    final_result['segment_name'] = os.path.basename(media)
    complete_result.append(final_result)

sys.stdout.write(str(complete_result))
