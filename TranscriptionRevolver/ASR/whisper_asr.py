import whisper

def apply_whisper(media_path, model_name="large-v3"):
    model = whisper.load_model(model_name)
    result = model.transcribe(media_path, language='es')
    sentence_ts = []
    for segment in result['segments']:
        sentence_ts.append({'start':segment['start'], 'end':segment['end'], 'text':segment['text']})
    return result['text'], sentence_ts