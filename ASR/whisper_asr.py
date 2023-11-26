import whisper
import os

media_volume = "/volume/media"
model_name = "base"
complete_result = {}
for media in sorted(os.listdir(media_volume)):

    model = whisper.load_model(model_name)
    result = model.transcribe(os.path.join(media_volume, media), language='es')
    sentence_ts = []
    for segment in result['segments']:
        sentence_ts.append({'start':segment['start'], 'end':segment['end'], 'text':segment['text']})
    final_result = {}
    final_result['text'] = result['text']
    final_result['sentences_ts'] = sentence_ts

    complete_result[media] = final_result

# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()