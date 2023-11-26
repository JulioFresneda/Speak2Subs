import torch
import os
from pydub import AudioSegment
from . import media


class VadConfig:
    def __init__(self, vad_folder, segmented=False, folder_name='VAD', suffix_segments='_segment'):
        self.suffix_segments = suffix_segments
        self.vad_folder = os.path.join(vad_folder, folder_name)

        if (not os.path.exists(self.vad_folder)):
            os.mkdir(self.vad_folder)

        self.segmented = segmented
        if self.segmented:
            self.segments_folder = os.path.join(self.vad_folder, 'segments')
            if (not os.path.exists(self.segments_folder)):
                os.mkdir(self.segments_folder)
        else:
            self.segments_folder = None


def apply_vad(my_media: media.Media, vad_config, max_speech_duration=float('inf'), segments=False):
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

    wav = read_audio(my_media.path, sampling_rate=sampling_rate)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate,
                                              max_speech_duration_s=max_speech_duration, return_seconds=False)

    vad_audio_path = os.path.join(vad_config.vad_folder, my_media.name)
    save_audio(vad_audio_path, collect_chunks(speech_timestamps, wav),
               sampling_rate=sampling_rate)

    ts_in_seconds = convert_samples_to_seconds(speech_timestamps, sampling_rate)
    my_vad = media.VAD(my_media, ts_in_seconds, vad_config)

    if segments:
        # Grouping timestamps
        vad_segments_ts = _split_timestamps_by_duration(speech_timestamps, max_speech_duration, sampling_rate)

        for i, st in enumerate(vad_segments_ts, start=0):
            st_in_seconds = convert_samples_to_seconds(st, sampling_rate)
            my_segment = media.Segment(my_vad, i, st_in_seconds, vad_config)
            my_vad.segments[my_segment.name] = my_segment

            save_audio(my_segment.path, collect_chunks(st, wav), sampling_rate=16000)

    my_media.vad = my_vad


def convert_samples_to_seconds(timestamp_dict_list, sampling_rate):
    new_timestamp_list = []
    for entry in timestamp_dict_list:
        new_entry = {
            'start': entry['start'] / sampling_rate,
            'end': entry['end'] / sampling_rate
        }
        new_timestamp_list.append(new_entry)
    return new_timestamp_list


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
