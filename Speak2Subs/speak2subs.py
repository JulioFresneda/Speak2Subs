from enum import Enum
import os  # Importing the os module for operating system-related functionality
import shutil
import json
import time

from Speak2Subs import container_manager
from Speak2Subs import vad
from Speak2Subs import media
from Speak2Subs import subtitle
from Speak2Subs import evaluate
from art import *


class ASR(Enum):
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    SPEECHBRAIN = 'speechbrain'
    TORCH = 'torch'
    WHISPER = 'whisper'
    SEAMLESS = 'seamless'

    @staticmethod
    def image(asr):
        image_names = {
            "nemo": "juliofresneda/s2s_nemo_asr_light:latest",
            "vosk": "juliofresneda/s2s_vosk_asr:latest",
            "whisper": "juliofresneda/s2s_whisper_asr:latest",
            "speechbrain": "juliofresneda/s2s_speechbrain_asr:latest",
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
    def __init__(self, dataset, asr):
        result = text2art("Speak2Subs")
        print(result)
        print("Let's sub that media! - Julio A. Fresneda -> github.com/JulioFresneda")
        print("---------------------------------------------------------------------")

        self._load_variables(dataset, asr)

        self.container_manager = container_manager.ContainerManager(self.asr_to_apply, self.host_volume_path)

    def _load_variables(self, dataset, asr):
        self.asr_to_apply = asr

        self.dataset = dataset
        self.host_volume_path = os.path.abspath(os.path.join(os.path.dirname(dataset.folder_path), 'host_volume'))

        if not os.path.exists(self.host_volume_path):
            os.mkdir(self.host_volume_path)

    def apply_processing(self):
        print(" ------------- Launching ASR ------------- ")
        times = {"execution_time":{}}
        for asr in self.asr_to_apply:
            times["execution_time"][asr.value] = {}
            for i, m in enumerate(self.dataset.media, start=1):
                start_timer = time.time()
                self._apply_asr_in_media(self.dataset.media[m], asr, index=i)
                execution_time = time.time() - start_timer
                times["execution_time"][asr.value][m] = execution_time
                print(" ------- Execution completed: " + str(int(execution_time)) + " seconds ------- ")
                print(" ------------- Generating VTT with " + asr.value + " ------------- ")
                self.dataset.media[m].generate_subtitles()
                self.dataset.media[m].predicted_subtitles.to_vtt(self.dataset.media[m], asr.value)
                self.dataset.media[m].reset_subtitles()

        shutil.rmtree(self.host_volume_path)
        shutil.rmtree(os.path.join(self.dataset.folder_path, "segment_groups"))
        with open(os.path.join(self.dataset.folder_path, "execution_times_" + self.dataset.name + ".json"), 'w') as json_file:
            json.dump(times, json_file)

    def _apply_asr_in_media(self, my_media, asr, index):
        print(" -- " + asr.value + " -> " + my_media.name + " (" + str(index) + "/" + str(
            len(self.dataset.media)) + ") -- ")
        print(" --->  Copying audio to container volume - KO <--- ", end='\r', flush=True)
        for segment_group in my_media.segments_groups:
            self._copy_segment_group_to_container_volume(segment_group, self.host_volume_path)
        print(" --->  Copying audio to container volume - OK <--- ")

        result = self.container_manager.execute_in_container(asr)
        print(" ---> Running transcription in container - OK <--- ")
        self._clean_volume()
        self._local_to_global_timestamps(result, my_media)

    def _local_to_global_timestamps(self, result, my_media):
        for seg_group in my_media.segments_groups:
            group_starts = seg_group.start
            token_list = []
            if 'words_ts' in result[seg_group.name].keys():
                token_list = result[seg_group.name]['words_ts']
                mode = "words"
            elif 'sentences_ts' in result[seg_group.name].keys():
                token_list = self._sentences_to_words(result[seg_group.name]['sentences_ts'], seg_group.group_duration)
                mode = "sentences"

            for token in token_list:
                last_end = group_starts
                silence = 0
                for segment in seg_group:
                    silence += segment.start - last_end
                    last_end = segment.end

                    local_start_in_global = token['start'] + group_starts + silence
                    local_end_in_global = token['end'] + group_starts + silence

                    if mode == "words":
                        limit = local_end_in_global
                    else:
                        limit = local_start_in_global
                    if segment.start <= limit <= segment.end:

                        if segment.predicted_subtitles is None:
                            segment.predicted_subtitles = subtitle.Subtitle()
                        tkn = subtitle.Token(local_start_in_global, local_end_in_global, token['token'] + " ")
                        segment.predicted_subtitles.add_token(tkn)
                        break
            to_remove = []
            for segment in seg_group:
                if segment.predicted_subtitles is None:
                    to_remove.append(segment)
            for item in to_remove:
                seg_group.segments.remove(item)


    def _sentences_to_words(self, sentence, duration):

        len_weighted = len(sentence) + sentence.count(',') + 2*sentence.count('.')
        ratio = duration / len_weighted

        tokenlist = sentence.split(" ")
        words = []
        for i, token in enumerate(tokenlist, start=0):
            weight = 1
            if (token[-1] == ','):
                weight = 2
            elif (token[-1] == '.'):
                weight = 3

            if(i == 0):
                start = 0
                end = ratio * (len(token) + weight)
            else:
                start = words[i-1]['end']
                end = words[i-1]['end'] + ratio * (len(token) + weight)

            words.append({'token':token, 'start':start, 'end':end})

        return words


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


def transcript(media_folder, asr='all', use_vad=True, segment=True, sentences=False, max_speech_duration=float('inf'),
               use_vtt_template=False):
    # Load dataset
    dataset = media.Dataset(media_folder, os.path.basename(media_folder), use_vtt_template)

    # Load asr
    asr_list = _load_asr(asr)
    s2s = Speak2Subs(dataset, asr_list)

    _pre_processing(dataset, max_speech_duration, use_vad, segment, sentences)
    _processing(s2s)
    _post_processing(dataset)


def _load_asr(asr):
    _asr = []
    if isinstance(asr, list):
        for asr_name in asr:
            for asr_obj in list(ASR):
                if (asr_name == asr_obj.value):
                    _asr.append(asr_obj)
    elif isinstance(asr, str):
        if (asr == 'all'):
            return list(ASR)
        for asr_obj in list(ASR):
            if (asr == asr_obj.value):
                _asr.append(asr_obj)
    return _asr


def _pre_processing(dataset, max_speech_duration, use_vad, segment, sentences):
    print(" ------------- Pre-processing media ------------- ")
    for m in dataset.media:
        print(" -- " + m + " -- ")
        mvad = vad.VAD(dataset.media[m], max_speech_duration, use_vad, segment, sentences)
        mvad.apply_vad()


def _processing(s2s: Speak2Subs):
    s2s.apply_processing()


def _post_processing(dataset):
    pass


def eval(reference, predicted):
    evaluate.evaluate_wer(reference, predicted)
