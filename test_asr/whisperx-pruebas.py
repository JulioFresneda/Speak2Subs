import whisperx
import gc 
import torch
import os

device = "cpu"
#audio_file =  "audio.wav"
batch_size = 16 # reduce if low on GPU mem
compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)
path = os.path.dirname(os.path.abspath(__file__))
print(path)
# 1. Transcribe with original whisper (batched)

gc.collect()
torch.cuda.empty_cache()


model = whisperx.load_model("base", device, compute_type=compute_type, language='es')
audio = whisperx.load_audio("../source_material/video1.wav")

result = model.transcribe(audio, batch_size=batch_size)
print(result["segments"]) # before alignment

# delete model if low on GPU resources
# import gc; gc.collect(); torch.cuda.empty_cache(); del model

# 2. Align whisper output
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

print(result["segments"]) # after alignment

# delete model if low on GPU resources
gc.collect()
torch.cuda.empty_cache()
del model_a
