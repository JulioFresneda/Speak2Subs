import whisperx
import gc
import torch
import sys
import os
import json

device = "cpu"
media_volume = "/volume/media"
batch_size = 16 # reduce if low on GPU mem
compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)

complete_result = {}
model = whisperx.load_model("base", device, compute_type=compute_type, language='es')



for media in sorted(os.listdir(media_volume)):
    gc.collect()
    torch.cuda.empty_cache()
    print(media)
    audio = whisperx.load_audio(os.path.join(media_volume,media))

    result = model.transcribe(audio, batch_size=batch_size, language='es')
    print(result["segments"])  # before alignment

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    result['sentences_ts'] = result.pop('segments')
    result['words_ts'] = result.pop('word_segments')
    complete_result[media] = result

# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()
