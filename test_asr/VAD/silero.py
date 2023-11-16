import torch

model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True,
                              onnx=False)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

wav = read_audio('../source_material/video1.wav', sampling_rate=16000)
# get speech timestamps from full audio file
speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)
print(speech_timestamps)

# merge all speech chunks to one audio
save_audio('../tests/only_speech.wav', collect_chunks(speech_timestamps, wav), sampling_rate=16000)
