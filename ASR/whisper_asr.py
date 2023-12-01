import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os


def save_progress(string):
    with open('/volume/progress.txt', 'w') as file:
        # Write a string to the file
        file.write(string)
        file.close()

media_volume = "/volume/media"
complete_result = {}

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=1,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)


for i, media in enumerate(sorted(os.listdir(media_volume)), start=1):
    result = pipe(os.path.join(media_volume, media), generate_kwargs={"language": "spanish"}, return_timestamps="word")


    final_result = {'text':result['text']}
    final_result['words_ts'] = []
    for chunk in result['chunks']:
        word = {}
        word['token'] = chunk['text']
        if(len(word['token']) > 0 and word['token'][0] == ' '):
            word['token'] = word['token'][1:]
        word['start'] = chunk['timestamp'][0]
        word['end'] = chunk['timestamp'][1]
        final_result['words_ts'].append(word)

    complete_result[media] = final_result
    print(result["text"])

    save_progress(str(i) + '/' + str(len(os.listdir(media_volume))))

with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()

save_progress("DONE")