import wave
import sys
import os

from vosk import Model, KaldiRecognizer, SetLogLevel

print("Hello from the vosk ASR image")

# You can set log level to -1 to disable debug messages
SetLogLevel(-1)

media_volume = "/vosk/media"
media_in_names = [f for f in os.listdir(media_volume) if os.path.isfile(os.path.join(media_volume, f))]
media_out_names = sys.argv[1:]

for media_name in media_out_names:

    print(media_name)
    wf = wave.open(os.path.join(media_volume,media_name), "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    model = Model(lang="es")



    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)


    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(rec.Result())
        else:
            print(rec.PartialResult())


    results = rec.FinalResult()
    print(results)
    print("$###########################################################################")



