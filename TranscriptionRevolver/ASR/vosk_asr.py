import wave
import sys
import os

from vosk import Model, KaldiRecognizer, SetLogLevel



# You can set log level to -1 to disable debug messages
SetLogLevel(0)

media_path = sys.argv[1]

if(not os.path.exists(media_path)):
    print("File does not exist")
    exit(1)


print(media_path)
wf = wave.open(media_path, "rb")
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



