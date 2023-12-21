from enum import Enum
import os  # Importing the os module for operating system-related functionality
import shutil
import json
import time

from Speak2Subs import container_manager
from Speak2Subs import vad
from Speak2Subs import media
from Speak2Subs import subtitle_tokens
from Speak2Subs import vtt_evaluator
from art import *


class ASR(Enum):
    SEAMLESS = 'seamless'
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    WHISPER = 'whisper'

    @staticmethod
    def image(asr):
        image_names = {
            "nemo": "juliofresneda/s2s_nemo_asr_light:latest",
            "vosk": "juliofresneda/s2s_vosk_asr:latest",
            "whisper": "juliofresneda/s2s_whisper_asr:latest",
            "whisperx": "juliofresneda/s2s_whisperx_asr:latest",
            "seamless": "juliofresneda/s2s_seamless_asr:latest"
        }
        if (type(asr) == ASR):
            return image_names[asr.value]
        elif (type(ASR) == str):
            return image_names[asr.value]
        else:
            return None


class Speak2Subs:
    def __init__(self, dataset: media.Dataset, asr, export_path: str, use_templates: bool):
        result = text2art("Speak2Subs")
        print(result)
        print("Let's sub that media! - Julio A. Fresneda -> github.com/JulioFresneda")
        print("---------------------------------------------------------------------")


        self._load_variables(dataset, asr, export_path, use_templates)
        self.container_manager = container_manager.ContainerManager(self.asr_to_apply, self.host_volume_path)

    def _load_variables(self, dataset: media.Dataset, asr, export_path: str, use_templates: bool):
        """
        Load necessary variables for the Speak2Subs application.

        Args:
            dataset (media.Dataset): Dataset class.
            asr: The Automatic Speech Recognition (ASR) system to apply.
            export_path (str): The path where the exported subtitles will be saved.
            use_templates (bool): A flag indicating whether to use templates during subtitling.
        """
        # Set the 'asr_to_apply' and 'use_templates' instance variables
        self.asr_to_apply = asr
        self.use_templates = use_templates

        # Set other instance variables related to paths and directories
        self.dataset = dataset
        # Create a cache path based on the directory of the current script
        self.cache_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "__cache__")
        # Set the export path as an absolute path
        self.export_path = os.path.abspath(export_path)
        # Set the host volume path within the cache path
        self.host_volume_path = os.path.join(self.cache_path, "host_volume")

        # Create necessary directories if they do not exist
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)
        else:
            # If the cache path already exists, remove its contents and recreate it
            shutil.rmtree(self.cache_path)
            os.mkdir(self.cache_path)

        # Create the export path directory if it does not exist
        if not os.path.exists(self.export_path):
            os.mkdir(self.export_path)

        # Create the host volume path directory if it does not exist
        if not os.path.exists(self.host_volume_path):
            os.mkdir(self.host_volume_path)

    def apply_processing(self):
        """
        Apply processing to the specified dataset using the configured ASR systems.

        Prints execution information and generates VTT subtitles for each ASR system.

        """
        print(" --------------------------- Launching ASR --------------------------- ")

        # Dictionary to store execution times
        times = {"execution_time": {}}

        # Loop through each ASR system to apply
        for asr in self.asr_to_apply:
            # Loop through each media item in the dataset
            for i, m in enumerate(self.dataset.media, start=1):
                # Initialize execution time tracking for the current media item
                if m not in times["execution_time"].keys():
                    times["execution_time"][m] = {}

                # Record the start time
                start_timer = time.time()

                # Apply ASR to the current media item
                self._apply_asr_in_media(self.dataset.media[m], asr, index=i)

                # Calculate and record execution time
                execution_time = time.time() - start_timer
                times["execution_time"][m][asr.value] = execution_time

                # Print execution completion information
                print(" ------- Execution completed: " + str(int(execution_time)) + " seconds")
                print(" ------- Generating VTT with " + asr.value)

                # Generate and save subtitles in VTT format
                self.dataset.media[m].generate_subtitles()
                self.dataset.media[m].predicted_subtitles.to_vtt(
                    self.dataset.media[m], asr.value, self.export_path, self.use_templates
                )

                # Reset subtitles for the current media item
                self.dataset.media[m].reset_subtitles()

            # Stop and remove the container for the current ASR system
            self.container_manager.containers[asr.value].stop()
            self.container_manager.containers[asr.value].remove()

        # Print completion message
        print(" ------------------------------- Done -------------------------------- ")

        # Remove temporary directories
        shutil.rmtree(self.host_volume_path)
        shutil.rmtree(self.cache_path)

        # Save execution times to a JSON file
        with open(os.path.join(self.export_path, "execution_times_" + self.dataset.name + ".json"), 'w') as json_file:
            json.dump(times, json_file)

    def _apply_asr_in_media(self, my_media, asr, index):
        """
        Apply Automatic Speech Recognition (ASR) to a specific media item.

        Args:
            my_media (Media): The media item to apply ASR to.
            asr (ASR): The ASR system to use.
            index (int): The index of the media item in the dataset.

        """
        # Print information about the ASR application for the current media item
        print(" ------- " + asr.value + " -> " + my_media.name + " (" + str(index) + "/" + str(
            len(self.dataset.media)) + ")")

        # Print progress information about copying audio to the container volume
        print(" ------>  Copying audio to container volume - KO", end='\r', flush=True)

        # Copy each segment group of the media item to the container volume
        for segment_group in my_media.segments_groups:
            self._copy_segment_group_to_container_volume(segment_group, self.host_volume_path)

        # Print completion message for copying audio
        print(" ------>  Copying audio to container volume - OK")

        # Execute ASR in the container and get the result
        result = self.container_manager.execute_in_container(asr)

        # Print completion message for running transcription in the container
        print(" ------> Running transcription in container - OK")

        # Clean up the container volume
        self._clean_volume()

        # Convert local timestamps to global timestamps
        self._local_to_global_timestamps(result, my_media)

    def _local_to_global_timestamps(self, result, my_media):
        """
        Convert local timestamps to global timestamps for the predicted subtitles.

        Args:
            result (dict): The result of the ASR system for the current media item.
            my_media (Media): The media item for which to convert timestamps.

        """
        # Iterate through each segment group in the media item
        for seg_group in my_media.segments_groups:
            # Calculate the starting time of the segment group
            group_starts = seg_group.start
            token_list = []

            # Check if ASR result contains word or sentence timestamps
            if 'words_ts' in result[seg_group.name].keys():
                token_list = result[seg_group.name]['words_ts']
                mode = "words"
            elif 'sentences_ts' in result[seg_group.name].keys():
                token_list = self._sentences_to_words(result[seg_group.name]['sentences_ts'], seg_group.group_duration)
                mode = "sentences"

            # Iterate through each token in the token list
            for token in token_list:
                last_end = group_starts
                silence = 0

                # Iterate through each segment in the segment group
                for segment in seg_group:
                    # Calculate the silence duration between segments
                    silence += segment.start - last_end
                    last_end = segment.end

                    # Calculate local start and end in global timestamps
                    local_start_in_global = token['start'] + group_starts + silence
                    local_end_in_global = token['end'] + group_starts + silence

                    # Check if the token falls within the current segment's time range
                    if mode == "words":
                        limit = local_end_in_global
                    else:
                        limit = local_start_in_global
                    if segment.start <= local_start_in_global <= segment.end:
                        # Create a subtitle token and add it to the segment's predicted subtitles
                        if segment.predicted_subtitles is None:
                            segment.predicted_subtitles = subtitle_tokens.Subtitle()
                        tkn = subtitle_tokens.Token(local_start_in_global, local_end_in_global, token['token'] + " ")
                        segment.predicted_subtitles.add_token(tkn)
                        break

            # Remove segments without predicted subtitles
            to_remove = []
            for segment in seg_group:
                if segment.predicted_subtitles is None:
                    to_remove.append(segment)
            for item in to_remove:
                seg_group.segments.remove(item)

    def _sentences_to_words(self, sentence, duration):
        """
        Convert a sentence into a list of words with corresponding timestamps.

        Args:
            sentence (str): The sentence to convert.
            duration (float): The duration of the sentence in seconds.

        Returns:
            list: A list of dictionaries representing words with 'token', 'start', and 'end' keys.

        """
        # Calculate a weighted length of the sentence
        len_weighted = len(sentence) + sentence.count(',') + 2 * sentence.count('.')
        # Calculate the ratio of duration to weighted length
        ratio = duration / len_weighted

        # Split the sentence into a list of tokens
        tokenlist = sentence.split(" ")
        words = []

        # Iterate through each token in the token list
        for i, token in enumerate(tokenlist, start=0):
            weight = 1
            # Adjust weight based on punctuation
            if token[-1] == ',':
                weight = 2
            elif token[-1] == '.':
                weight = 3

            # Calculate start and end timestamps for the word
            if i == 0:
                start = 0
                end = ratio * (len(token) + weight)
            else:
                start = words[i - 1]['end']
                end = words[i - 1]['end'] + ratio * (len(token) + weight)

            # Append word information to the list
            words.append({'token': token, 'start': start, 'end': end})

        return words

    def _copy_segment_group_to_container_volume(self, segment_group, host_volume_path):
        """
        Copy the audio file of a segment group to the container's volume.

        Args:
            segment_group (SegmentGroup): The segment group whose audio file is to be copied.
            host_volume_path (str): The path to the host volume where the audio file will be copied.

        """
        # Create the host media path within the host volume path
        host_media_path = os.path.join(host_volume_path, 'media')

        # Create the host media path if it does not exist
        if not os.path.exists(host_media_path):
            os.makedirs(host_media_path)

        # Define the destination file path within the host media path
        dest_file = os.path.join(host_media_path, segment_group.name)

        # Copy the audio file from the segment group to the host media path
        shutil.copy2(segment_group.path, dest_file)

    def _clean_volume(self):
        """
        Clean up the contents of the container's volume.

        This method removes all files and directories within the host volume path.

        """
        # Iterate through each item in the host volume path
        for filename in os.listdir(self.host_volume_path):
            file_path = os.path.join(self.host_volume_path, filename)
            try:
                # Check if the item is a file or a symbolic link
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    # Remove the file or symbolic link
                    os.unlink(file_path)
                # Check if the item is a directory
                elif os.path.isdir(file_path):
                    # Remove the directory and its contents
                    shutil.rmtree(file_path)
            except Exception as e:
                # Print an error message if deletion fails
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def transcript(media_path, export_path, asr='all', use_vad=True, segment=True, group_segments=True,
               max_speech_duration=float('inf'),
               use_vtt_template=False, reduce_noise=False):
    """
    Perform the entire transcription process on a media folder.

    Args:
        media_path (str): The path to the media folder or mp4/wav file.
        export_path (str): The path where the exported subtitles will be saved.
        asr: The ASR system(s) to use for transcription. Default is 'all'.
        use_vad (bool): Flag indicating whether to use Voice Activity Detection. Default is True.
        segment (bool): Flag indicating whether to segment audio. Default is True.
        group_segments (bool): Flag indicating whether to group segments and don't transcribe at the sentence level. Default is True.
        max_speech_duration (float): Maximum duration for a segment. Default is infinity.
        use_vtt_template (bool): Flag indicating whether to use VTT template for subtitles. Default is False.
        reduce_noise (bool): Flag indicating whether to reduce noise in audio. Default is False.
    """
    # Load dataset
    dataset = media.Dataset(media_path, os.path.basename(media_path), use_vtt_template)

    # Load ASR systems
    asr_list = _load_asr(asr)

    # Initialize Speak2Subs instance
    s2s = Speak2Subs(dataset, asr_list, export_path, use_vtt_template)

    print(" ------- VAD -> " + str(use_vad))
    print(" ------- Segment -> " + str(segment))
    print(" ------- Group segments -> " + str(group_segments))
    print(" ------- MSD -> " + str(max_speech_duration))
    print(" ------- ASR -> " + str(asr))
    print(" ------- Reduce noise -> " + str(reduce_noise))
    print(" ------- Use VTT template -> " + str(use_vtt_template))







    # Perform pre-processing steps
    _pre_processing(dataset, max_speech_duration, use_vad, segment, group_segments, s2s.cache_path, reduce_noise)

    # Perform main processing steps
    _processing(s2s)

    # Perform post-processing steps
    _post_processing(dataset)



def _load_asr(asr):
    """
    Load ASR systems based on the provided input.

    Args:
        asr (str or list): The ASR system(s) to load. It can be a string, a list of strings, or 'all'.

    Returns:
        list: A list of ASR system objects.

    """
    _asr = []

    # Check if 'asr' is a list
    if isinstance(asr, list):
        # Iterate through each ASR name in the list
        for asr_name in asr:
            # Check if the ASR name corresponds to a valid ASR system
            for asr_obj in list(ASR):
                if asr_name == asr_obj.value:
                    _asr.append(asr_obj)

    # Check if 'asr' is a string
    elif isinstance(asr, str):
        # Check if 'asr' is set to 'all'
        if asr == 'all':
            return list(ASR)

        # Iterate through each ASR system to find a match with the provided name
        for asr_obj in list(ASR):
            if asr == asr_obj.value:
                _asr.append(asr_obj)

    return _asr


def _pre_processing(dataset, max_speech_duration, use_vad, segment, group_segments, cache_path, reduce_noise):
    """
    Perform pre-processing steps on each media item in the dataset.

    Args:
        dataset (media.Dataset): The dataset containing media items.
        max_speech_duration (float): Maximum duration for a segment.
        use_vad (bool): Flag indicating whether to use Voice Activity Detection.
        segment (bool): Flag indicating whether to segment audio.
        group_segments (bool): Flag indicating whether to group segments and don't transcribe at the sentence level.
        cache_path (str): The path to the cache directory.
        reduce_noise (bool): Flag indicating whether to reduce noise in audio.

    """
    print(" ------- Pre-processing media")

    # Iterate through each media item in the dataset
    for m in dataset.media:
        print(" ------- " + m)

        # Initialize VAD for the current media item
        mvad = vad.VAD(dataset.media[m], max_speech_duration, use_vad, segment, group_segments, reduce_noise)

        # Apply Voice Activity Detection (VAD) to the current media item and save the result in the cache
        mvad.apply_vad(cache_path)


def _processing(s2s: Speak2Subs):
    s2s.apply_processing()


def _post_processing(dataset):
    pass


def evaluateFolder(dataset_folder_path, results_folder_path, dataset_name):
    if dataset_name == None:
        dataset_name = os.path.basename(dataset_folder_path)
    vtt_evaluator.Evaluator(dataset_name, os.path.abspath(dataset_folder_path),
                                        os.path.abspath(results_folder_path))

def evaluatePair(ref_vtt_path, pred_vtt_path):
    output = vtt_evaluator.evaluate_error_metrics(ref_vtt_path, pred_vtt_path)
    return output

def evaluateCompliance(vtt_path):
    comp = vtt_evaluator.evaluate_compliance(vtt_path)
    return comp
