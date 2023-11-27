from enum import Enum
import os  # Importing the os module for operating system-related functionality
import shutil
import json

from . import container_manager
from . import vad
from . import media
from . import subtitle


class ASRNames(Enum):
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    SPEECHBRAIN = 'speechbrain'
    TORCH = 'torch'
    WHISPER = 'whisper'

class TranscriptMode(Enum):
    ORIGINAL_MODE = 'original_mode'
    VAD_MODE = 'vad_mode'
    VAD_AND_SEGMENTED_MODE = 'vad_and_segmented_mode'


class Speak2Subs:
    def __init__(self, dataset, asr, config):

        if isinstance(asr, str) and asr == 'all':
            self.asr_to_apply = list(ASRNames)
        elif isinstance(asr, list) and all(item in ASRNames for item in asr):
            self.asr_to_apply = asr.copy()
        elif isinstance(asr, ASRNames):
            self.asr_to_apply = [asr]

        self.conf = config
        self.dataset = dataset
        self.host_volume_path = os.path.abspath(os.path.join(os.path.dirname(dataset.folder_path), 'host_volume'))
        self.transcript_mode = TranscriptMode.ORIGINAL_MODE

        if not os.path.exists(self.host_volume_path):
            os.mkdir(self.host_volume_path)

        self.container_manager = container_manager.ContainerManager(self.asr_to_apply, self.host_volume_path,
                                                                    self.conf['image_names'])

    def launch_asr(self):
        for asr in self.asr_to_apply:
            for k in self.dataset.media:
                my_media = self.dataset.media[k]
                if (self.transcript_mode == TranscriptMode.ORIGINAL_MODE):
                    self._copy_media_to_container_volume(my_media, self.host_volume_path)
                elif (self.transcript_mode == TranscriptMode.VAD_MODE):
                    self._copy_media_to_container_volume(my_media.vad, self.host_volume_path)
                else:
                    for segment in my_media.vad.segments.keys():
                        self._copy_media_to_container_volume(my_media.vad.segments[segment], self.host_volume_path)

                result = self.container_manager.execute_in_container(asr)
                self._clean_volume()
                self._cook_result(result, my_media)

    def _cook_result(self, result, my_media):
        if(self.transcript_mode == TranscriptMode.VAD_AND_SEGMENTED_MODE):
            last_global_end = 0
            for segment in result.keys():
                text = result[segment]['text']
                words_ts = None
                if('words_ts' in result[segment].keys()):
                    words_ts = result[segment]['words_ts']
                seg_ts = None
                if ('segments_ts' in result[segment].keys()):
                    seg_ts = result[segment]['segments_ts']

                vad_ts = my_media.vad.original_timestamps
                sub = subtitle.Subtitle(text, words_ts, seg_ts, vad_ts, last_global_end)
                my_media.add_segment_subtitle(sub, segment)
                last_global_end = sub.last_global_end








    def _copy_media_to_container_volume(self, my_media, host_volume_path):

        host_media_path = os.path.join(host_volume_path, 'media')
        if not os.path.exists(host_media_path):
            os.makedirs(host_media_path)

        dest_file = os.path.join(host_media_path, my_media.name)
        shutil.copy2(my_media.path, dest_file)

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

    def export_subtitles_to_vtt_eval(self):
        for my_media in self.dataset.media:
            original_subs_path = self.dataset.media[my_media].original_subtitles_path
            original_subs = self._load_subs(original_subs_path)
            predicted_subs = self.dataset.media[my_media].predicted_subtitles

            predicted_subs_adjusted = []
            for original_sub in original_subs:
                sub_adjusted = {'start':original_sub['start'], 'end':original_sub['end'], 'text':""}
                for sub in predicted_subs:
                    for word in sub.original_word_timestamps:
                        if(original_sub['start'] <= word['start'] <= original_sub['end']):
                            sub_adjusted['text'] += word['word'] + " "
                predicted_subs_adjusted.append(sub_adjusted)


            print(predicted_subs)




    def _load_subs(self, subs_path):

        subtitles_with_timestamps = []

        with open(subs_path, 'r') as file:
            lines = file.readlines()
            line_type = "timestamp"
            for line in lines[2:]:
                if (line == '\n'):
                    line_type = "linebreak"
                    subtitles_with_timestamps.append(ts.copy())
                    ts = {}
                if(line_type == "linebreak"):
                    line_type = "timestamp"
                elif(line_type == "timestamp"):
                    ts = self._load_subs_timestamps(line)
                    line_type = "text"
                elif(line_type == "text"):
                    try:
                        ts['text'] += line.replace("\n", " ")
                    except:
                        ts['text'] = line.replace("\n", " ")

        return subtitles_with_timestamps





    def _load_subs_timestamps(self, line):
        start, end = line.split(" --> ")
        start_h, start_m, start_s = map(float, start.split(":"))
        end_h, end_m, end_s = map(float, end.split(":"))

        start_seconds = start_h * 3600 + start_m * 60 + start_s
        end_seconds = end_h * 3600 + end_m * 60 + end_s

        return {
            "start": round(start_seconds, 3),
            "end": round(end_seconds, 3)
        }









def transcript(dataset, asr='all', use_vad=True, segment=True, max_speech_duration=float('inf'), eval_mode = False):
    """

    :type segment: object
    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_path, './configuration.json'), 'r') as file:
        config = json.load(file)

    s2s = Speak2Subs(dataset, asr, config)

    if not isinstance(dataset, media.Dataset):
        raise ValueError("Unsupported input type")



    for m in dataset.media:
        mvad = vad.VAD(dataset.media[m], max_speech_duration, segment)
        mvad.apply_vad()

    s2s.launch_asr()
    if(eval_mode):
        s2s.export_subtitles_to_vtt_eval()


