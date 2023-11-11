from huggingsound import SpeechRecognitionModel

model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")
audio_paths = ["audios/audio.wav", "audios/carmen.wav"]

transcriptions = model.transcribe(audio_paths)
print(transcriptions[0])
print(transcriptions[1])