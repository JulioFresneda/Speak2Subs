import torch
import os
from pydub import AudioSegment
import noisereduce as nr

from Speak2Subs import media


class VAD:
    def __init__(self, my_media, max_speech_duration=float('inf'), use_vad=True, segment=True, group_segments=True, reduce_noise=True):
        """
        Initialize the VAD (Voice Activity Detection) configuration.

        Args:
            my_media (Media): The media item for which VAD will be applied.
            max_speech_duration (float): Maximum duration for a segment. Default is infinity.
            use_vad (bool): Flag indicating whether to use Voice Activity Detection. Default is True.
            segment (bool): Flag indicating whether to segment audio. Default is True.
            group_segments (bool): Flag indicating whether to group segments and don't transcribe at the sentence level. Default is True.
            reduce_noise (bool): Flag indicating whether to reduce noise in audio. Default is True.

        """
        # Store input parameters as instance variables
        self.media = my_media
        self.max_speech_duration = max_speech_duration
        self.use_vad = use_vad
        self.segment = segment
        self.group_segments = group_segments
        self.reduce_noise = reduce_noise

        # If segmentation is disabled, set max_speech_duration to infinity
        if not self.segment:
            self.max_speech_duration = float('inf')

    def apply_vad(self, cache_path):
        """
        Apply Voice Activity Detection (VAD) to the media item and save the result.

        Args:
            cache_path (str): The path to the cache directory.

        """
        # Store the cache path as an instance variable
        self.cache_path = cache_path
        # Set the sampling rate to 16000
        self.sampling_rate = 16000

        # Apply the VAD model to the media item
        self._apply_model()

        # Load and process the detected segments
        self._load_segments()
        self._group_segments()

        # Save the VAD segments to a file
        self._save_segments_to_file()

    def _apply_model(self):
        """
        Apply the VAD model to detect speech segments in the audio file.

        Uses the Silero VAD model for Voice Activity Detection.

        """
        # Load Silero VAD model and utilities
        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False,
            verbose=False
        )

        # Extract utility functions from the loaded module
        (get_speech_timestamps,
         self.save_audio,
         read_audio,
         VADIterator,
         self.collect_chunks) = utils

        # Read the audio file and apply noise reduction if specified
        self.wav = read_audio(self.media.path, sampling_rate=self.sampling_rate)
        if self.reduce_noise:
            self.wav = reduce_noise(self.wav)

        # Check if Voice Activity Detection (VAD) should be applied
        if self.use_vad:
            print(" ------> Voice Activity Detection - KO", end='\r', flush=True)
            self.speech_timestamps = get_speech_timestamps(
                self.wav,
                model,
                sampling_rate=self.sampling_rate,
                max_speech_duration_s=self.max_speech_duration,
                return_seconds=False
            )
            print(" ------> Voice Activity Detection - OK")

        else:
            print(" ------> Voice Activity Detection - NO")
            audio_len = self.wav.shape[0]

            # Check if segmentation is enabled and the audio length is greater than the specified duration
            if self.segment and self.max_speech_duration <= audio_len:
                print(" ------> Segmentation - KO", end='\r', flush=True)
                self.speech_timestamps = []
                for i in range(0, int(audio_len / self.max_speech_duration) + 1, self.sampling_rate):
                    self.speech_timestamps.append({'start': int(i * self.max_speech_duration),
                                                   'end': int((i + self.sampling_rate) * self.max_speech_duration)})
                self.speech_timestamps[-1]['end'] = audio_len
                print(" ------> Segmentation - OK")

            else:
                print(" ------> Segmentation - NO")
                self.speech_timestamps = [{'start': 0, 'end': audio_len}]

    def _load_segments(self):
        """
        Load speech segments based on the detected speech timestamps.

        """
        segments = []

        # Iterate through each speech timestamp and create corresponding Segment objects
        for ts in self.speech_timestamps:
            # Convert timestamps from samples to seconds
            start_time = ts['start'] / self.sampling_rate
            end_time = ts['end'] / self.sampling_rate

            # Create a Segment object and append it to the segments list
            segments.append(media.Segment(start_time, end_time, ts))

        # Store the list of segments as an instance variable
        self.segments = segments

    def _group_segments(self):
        """
        Group speech segments based on the specified conditions.

        """
        result = []
        self.segment_groups = []

        # Check if grouping by sentences is disabled
        if self.group_segments and self.segments:
            print(" ------> Group segments - KO", end='\r', flush=True)
            current_list = []

            # Iterate through each segment and group them based on duration constraints
            for segment in self.segments:
                duration_so_far = sum([sg.end - sg.start for sg in current_list])
                segment_duration = segment.end - segment.start

                # Check if adding the current segment exceeds the maximum speech duration
                if duration_so_far + segment_duration <= self.max_speech_duration:
                    current_list.append(segment)
                else:
                    result.append(current_list)
                    current_list = [segment]

            # Add the remaining segments to the result
            if current_list:
                result.append(current_list)
            print(" ------> Group segments - OK")

        else:
            print(" ------> Group segments - NO")

            # Group each segment individually
            for seg in self.segments:
                result.append([seg])

        # Create a folder for segment groups in the cache path
        self.segment_groups_folder = os.path.join(self.cache_path, "segment_groups")
        if not os.path.exists(self.segment_groups_folder):
            os.mkdir(self.segment_groups_folder)

        # Convert the result to media groups and store them as instance variables
        for i, r in enumerate(result, start=0):
            self.segment_groups.append(self._group_to_media_group(r, i))
        self.media.segments_groups = self.segment_groups

    def _group_to_media_group(self, group, index):
        """
        Convert a group of segments to a media group.

        Args:
            group (list): List of speech segments.
            index (int): Index of the media group.

        Returns:
            media.SegmentGroup: A media group containing the speech segments.

        """
        # Generate a path for the segment group
        generated_path = os.path.join(
            self.segment_groups_folder,
            f"{self.media.name.split('.')[0]}_segment_{index}.wav"
        )

        # Create a SegmentGroup object and return it
        return media.SegmentGroup(group, generated_path)

    def _save_segments_to_file(self):
        """
        Save audio segments from each segment group to individual files.

        """
        # Iterate through each segment group
        for i, st in enumerate(self.segment_groups, start=0):
            print(" ------> Saving audios - " + str(i) + "/" + str(len(self.segment_groups)) + "   ", end='\r',
                  flush=True)

            # Create a list of timestamp dictionaries for each segment in the group
            ts_list = [seg.ts_dict for seg in st]

            # Save the audio file for the segment group
            self.save_audio(st.path, self.collect_chunks(ts_list, self.wav), sampling_rate=16000)

    def _collect_chunks_with_silence(self, tss, wav: torch.Tensor):
        """
        Collect audio chunks with silence based on provided timestamps.

        Args:
            tss (list): List of timestamp dictionaries for each segment.
            wav (torch.Tensor): The original audio waveform.

        Returns:
            torch.Tensor: Concatenated audio chunks with silence.

        """
        chunks = []
        five_seconds_length = int(self.sampling_rate * 3)
        first_5_seconds_tensor = wav[:five_seconds_length]
        silence_tensor = torch.zeros_like(first_5_seconds_tensor)

        # Iterate through each timestamp dictionary and collect chunks with silence
        for i in tss:
            wav_with_sil = wav[i['start']: i['end']]
            result_tensor = torch.cat([wav_with_sil, silence_tensor])

            chunks.append(result_tensor)

        # Concatenate all collected chunks
        return torch.cat(chunks)


def reduce_noise(waveform):
    # Convert PyTorch tensor to NumPy array
    audio_array = waveform.numpy()
    # Perform noise reduction
    reduced_audio = nr.reduce_noise(audio_array, 16000, device="cpu")
    # Convert back to PyTorch tensor
    waveform = torch.from_numpy(reduced_audio)

    return waveform
