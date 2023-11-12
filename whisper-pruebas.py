import whisper

model = whisper.load_model("large-v3")
result = model.transcribe("audios/bdias.wav")
print(result)