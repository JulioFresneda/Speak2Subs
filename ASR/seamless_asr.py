import torch
import torchaudio
import os
from seamless_communication.models.inference import Translator

import wave

def get_audio_duration(file_path):
    with wave.open(file_path, 'rb') as audio_file:
        frames = audio_file.getnframes()
        rate = audio_file.getframerate()
        duration_seconds = frames / float(rate)

    return duration_seconds



media_volume = "/volume/media"
complete_result = {}
translator = Translator(
    "seamlessM4T_medium",
    "vocoder_36langs",
    torch.device("cpu"),
    torch.float16
)
for media in sorted(os.listdir(media_volume)):
    media_path = os.path.join(media_volume, media)
    text, _, _ = translator.predict(media_path, "asr", "spa")
    complete_result[media] = {"sentences_ts":[{'start':0, 'end':get_audio_duration(media_path), 'token':str(text)}]}

# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()






