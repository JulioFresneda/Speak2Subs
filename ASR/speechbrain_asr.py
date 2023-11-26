import os


from speechbrain.pretrained import EncoderDecoderASR

media_volume = "/volume/media"

complete_result = {}
asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-commonvoice-14-es")

for media in sorted(os.listdir(media_volume)):
    trans = asr_model.transcribe_file(os.path.join(media_volume,media))
    complete_result[media] = trans

# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()