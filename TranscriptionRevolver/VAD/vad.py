import torch
import os
def apply_vad(file_path):
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=True,
                                  onnx=False)

    (get_speech_timestamps,
     save_audio,
     read_audio,
     VADIterator,
     collect_chunks) = utils

    wav = read_audio(file_path, sampling_rate=16000)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)
    print(speech_timestamps)

    vad_name = _apply_suffix('_VAD', file_path)
    save_audio(vad_name, collect_chunks(speech_timestamps, wav), sampling_rate=16000)

def _apply_suffix(suffix, file_path):

    # Split the file path into directory, filename, and extension
    directory, filename_ext = os.path.split(file_path)
    filename, extension = os.path.splitext(filename_ext)

    # Add the suffix to the filename
    new_filename = f"{filename}{suffix}{extension}"

    # Construct the new file path
    new_file_path = os.path.join(directory, new_filename)
    return new_file_path