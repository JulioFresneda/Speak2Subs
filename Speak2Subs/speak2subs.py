from enum import Enum
import os  # Importing the os module for operating system-related functionality
import shutil
import json

from . import container_manager
from . import vad
from . import media
from . import subtitle
from . import eval
from art import *



class ASRNames(Enum):
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    SPEECHBRAIN = 'speechbrain'
    TORCH = 'torch'
    WHISPER = 'whisper'
    SEAMLESS = 'seamless'


class Speak2Subs:
    def __init__(self, dataset, asr, config):
        result = text2art("Speak2Subs")
        print(result)
        print("Let's sub that media! - Julio A. Fresneda -> github.com/JulioFresneda")
        print("---------------------------------------------------------------------")

        if isinstance(asr, str) and asr == 'all':
            self.asr_to_apply = list(ASRNames)
        elif isinstance(asr, list) and all(item in ASRNames for item in asr):
            self.asr_to_apply = asr.copy()
        elif isinstance(asr, ASRNames):
            self.asr_to_apply = [asr]

        self.conf = config
        self.dataset = dataset
        self.host_volume_path = os.path.abspath(os.path.join(os.path.dirname(dataset.folder_path), 'host_volume'))

        if not os.path.exists(self.host_volume_path):
            os.mkdir(self.host_volume_path)

        self.container_manager = container_manager.ContainerManager(self.asr_to_apply, self.host_volume_path,
                                                                    self.conf['image_names'])

    def launch_asr(self):
        print(" ------------- Launching ASR ------------- ")
        vtt_files = {}
        for asr in self.asr_to_apply:
            vtt_files[asr.value] = {}
            for i, k in enumerate(self.dataset.media, start=1):
                print(" -- " + asr.value + " -> " + k + " (" + str(i) + "/" + str(len(self.dataset.media)) + ") -- ")
                my_media = self.dataset.media[k]
                print(" --->  Copying audio to container volume - KO <--- ", end='\r', flush=True)
                for segment_group in my_media.segments_groups:
                    self._copy_segment_group_to_container_volume(segment_group, self.host_volume_path)
                print(" --->  Copying audio to container volume - OK <--- ")

                result = self.container_manager.execute_in_container(asr)
                print(" ---> Running transcription in container - OK <--- ")
                self._clean_volume()
                self._local_to_global_timestamps(result, my_media)
                print(" ------------- Generating VTT ------------- ")
                my_media.generate_subtitles()
                vtt_files[asr.value][k] = my_media.predicted_subtitles.to_vtt(my_media)

        shutil.rmtree(self.host_volume_path)
        shutil.rmtree(os.path.join(self.dataset.folder_path, "segment_groups"))
        return vtt_files


    def _local_to_global_timestamps(self, result, my_media):
        for seg_group in my_media.segments_groups:
            group_starts = seg_group.start
            token_list = []
            if 'words_ts' in result[seg_group.name].keys():
                token_list = result[seg_group.name]['words_ts']
                mode = "words"
            elif 'sentences_ts' in result[seg_group.name].keys():
                token_list = result[seg_group.name]['sentences_ts']
                mode = "sentences"

            for token in token_list:
                last_end = group_starts
                silence = 0
                for segment in seg_group:
                    silence += segment.start - last_end
                    last_end = segment.end

                    local_start_in_global = token['start'] + group_starts + silence
                    local_end_in_global = token['end'] + group_starts + silence

                    if(mode == "words"):
                        limit = local_end_in_global
                    else:
                        limit = local_start_in_global
                    if segment.start <= limit <= segment.end:

                        if segment.predicted_subtitles is None:
                            segment.predicted_subtitles = subtitle.Subtitle()
                        tkn = subtitle.Token(local_start_in_global, local_end_in_global, token['token'] + " ")
                        segment.predicted_subtitles.add_token(tkn)
                        break





    def _copy_segment_group_to_container_volume(self, segment_group, host_volume_path):

        host_media_path = os.path.join(host_volume_path, 'media')
        if not os.path.exists(host_media_path):
            os.makedirs(host_media_path)

        dest_file = os.path.join(host_media_path, segment_group.name)
        shutil.copy2(segment_group.path, dest_file)

    def _clean_volume(self):
        for filename in os.listdir(self.host_volume_path):
            file_path = os.path.join(self.host_volume_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def transcript(dataset, asr='all', use_vad=True, segment=True, sentences=False, max_speech_duration=float('inf'), eval_mode=False):
    """

    :param eval_mode:
    :param max_speech_duration:
    :param use_vad:
    :param asr:
    :param dataset:
    :type segment: object
    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_path, './configuration.json'), 'r') as file:
        config = json.load(file)

    s2s = Speak2Subs(dataset, asr, config)

    if not isinstance(dataset, media.Dataset):
        raise ValueError("Unsupported input type")

    msd = max_speech_duration
    if (not segment):
        msd = float('inf')

    print(" ------------- Pre-processing media ------------- ")
    for m in dataset.media:
        print(" -- " + m + " -- ")
        mvad = vad.VAD(dataset.media[m], msd, use_vad, segment, sentences)
        mvad.apply_vad()




    return s2s.launch_asr()



def evaluate(reference_vtt_path, predicted_vtt_path):
    evaluator = eval.Evaluator(reference_vtt_path, predicted_vtt_path)