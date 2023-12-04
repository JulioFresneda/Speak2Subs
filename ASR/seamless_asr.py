from transformers import SeamlessM4Tv2Model
import torch
from transformers import AutoProcessor
import os
from datasets import load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = model.to(device)

def save_progress(string):
    with open('/volume/progress.txt', 'w') as file:
        # Write a string to the file
        file.write(string)
        file.close()

media_volume = "/volume/media"
complete_result = {}



dataset = load_dataset("/volume/media", "hi_in", split="train", streaming=True)
dataset_iter = iter(dataset)
for i, media in enumerate(sorted(os.listdir(media_volume)), start=1):
    audio_sample = next(dataset_iter)["audio"]

    audio_inputs = processor(audios=audio_sample["array"], sampling_rate=16000, return_tensors="pt").to(device)

    output_tokens = model.generate(**audio_inputs, tgt_lang="spa", generate_speech=False)
    translated_text_from_audio = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    complete_result[media] = {'sentences_ts':translated_text_from_audio}
    save_progress(str(i) + '/' + str(len(os.listdir(media_volume))))

# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()

save_progress("DONE")