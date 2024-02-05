import whisperx
import gc
import torch
import sys
import os
import json

device = "cuda" if torch.cuda.is_available() else "cpu"
media_volume = "/volume/media"
batch_size = 16 # reduce if low on GPU mem
compute_type = "float16" if torch.cuda.is_available() else "int8" # change to "int8" if low on GPU mem (may reduce accuracy)

complete_result = {}
model = whisperx.load_model("large-v2", device, compute_type=compute_type, language='es')

def save_progress(string):
    with open('/volume/progress.txt', 'w') as file:
        # Write a string to the file
        file.write(string)
        file.close()

for i, media in enumerate(sorted(os.listdir(media_volume)), start=1):
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
    for r in result['words_ts']:
        r['token'] = r.pop('word')

    for j, token in enumerate(result['words_ts'], start=0):
        if('start' not in token.keys()):
            if(j==0):
                token['start'] = 0
            else:
                token['start'] = result['words_ts'][j-1]['end']
        if ('end' not in token.keys()):
            token['end'] = token['start'] + 0.01

        if('score' not in token.keys()):
            token['score'] = 0

    complete_result[media] = result
    save_progress(str(i) + '/' + str(len(os.listdir(media_volume))))


# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()

save_progress("DONE")