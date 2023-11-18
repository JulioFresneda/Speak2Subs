import torch
import os
from pydub import AudioSegment
def apply_vad(media, max_speech_duration=float('inf'), split=False):
    sampling_rate = 16000

    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=False,
                                  onnx=False)

    (get_speech_timestamps,
     save_audio,
     read_audio,
     VADIterator,
     collect_chunks) = utils

    wav = read_audio(media.original_media_path, sampling_rate=sampling_rate)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate, max_speech_duration_s=max_speech_duration)
    print(speech_timestamps)

    vad_path = _modify_path('_VAD', 'VAD', media.original_media_path)
    save_audio(vad_path, collect_chunks(speech_timestamps, wav), sampling_rate=sampling_rate)

    media.add_vad(vad_path, speech_timestamps)

    if(split):

        # Grouping timestamps
        vad_segments_ts = _split_timestamps_by_duration(speech_timestamps, max_speech_duration, sampling_rate)
        vad_segments_paths = []

        for i, st in enumerate(vad_segments_ts, start=0):
            segment_path = _modify_path('_VAD_segment_' + str(i), 'segments', vad_path)
            save_audio(segment_path, collect_chunks(st, wav), sampling_rate=16000)
            vad_segments_paths.append(segment_path)

        media.add_vad_segments(vad_segments_paths=vad_segments_paths, vad_segments_ts=vad_segments_ts)

    return vad_path, speech_timestamps


def _split_timestamps_by_duration(timestamps, max_duration, sampling_rate):
    max_duration *= sampling_rate  # Convert max_duration from seconds to samples (assuming 16kHz sampling rate)
    result = []
    current_list = []

    for timestamp in timestamps:
        duration_so_far = sum([ts['end'] - ts['start'] for ts in current_list])
        timestamp_duration = timestamp['end'] - timestamp['start']

        if duration_so_far + timestamp_duration <= max_duration:
            current_list.append(timestamp)
        else:
            result.append(current_list)
            current_list = [timestamp]

    if current_list:
        result.append(current_list)

    return result



def _split_audio(file_path, timestamps):
    # Load your audio file using pydub
    audio = AudioSegment.from_file(file_path, format="wav")

    # Duration in milliseconds for each segment (30 seconds = 30,000 milliseconds)
    segment_duration = 30 * 1000  # 30 seconds in milliseconds

    _ts = []
    for se in timestamps:
        _ts.append((se['start'], se['end']))

    # Split the audio using timestamps
    for i, (start, end) in enumerate(_ts, start=1):
        segment = audio[start:end]
        segment.export(f"_VAD_segment_{i}.wav", format="wav")



def _modify_path(suffix, new_folder_name, file_path):

    # Split the file path into directory, filename, and extension
    directory, filename_ext = os.path.split(file_path)
    filename, extension = os.path.splitext(filename_ext)
    extension = ".wav"

    # New folder name
    new_folder = new_folder_name

    # Construct the path for the 'VAD' subfolder
    vad_folder = os.path.join(directory, new_folder)

    # Check if the 'VAD' subfolder exists, if not, create it
    if not os.path.exists(vad_folder):
        os.makedirs(vad_folder)

    # Add the suffix to the filename
    new_filename = f"{filename}{suffix}{extension}"

    # Construct the new file path
    new_file_path = os.path.join(vad_folder, new_filename)
    return new_file_path