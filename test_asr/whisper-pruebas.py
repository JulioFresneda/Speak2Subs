import whisper

model = whisper.load_model("large-v3")
result = model.transcribe("tests/bdias.wav")
print(result)