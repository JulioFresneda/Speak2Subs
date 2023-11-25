import os.path
import random
from moviepy.editor import AudioFileClip
import logging

class Media:
    def __init__(self, path):
        self.path = path
        self.folder = os.path.dirname(os.path.abspath(path))
        self.name = os.path.basename(path)
        self.vad = None


class VAD(Media):
    def __init__(self, original_media, timestamps, vad_config):
        self.original = original_media
        super().__init__(os.path.join(vad_config.vad_folder, original_media.name))
        original_media.vad = self
        self.timestamps = timestamps
        self.segments = []

class Segment(Media):
    def __init__(self, vad_media, index, timestamps, vad_config):
        name, extension = vad_media.name.split('.')
        name = name + vad_config.suffix_segments
        name = name + "_" + str(index) + "." + extension
        super().__init__(os.path.join(vad_config.segments_folder,name))
        self.timestamps = timestamps
        self.segment_of = vad_media




class Dataset:
    def __init__(self, folder_path, name = None):
        if(name != None):
            self.name = name

        # Always keep order
        self.media = {}
        self.folder_path = os.path.abspath(folder_path)

        self._load_media_folder(self.folder_path)
        self._order_media()

    def _order_media(self):
        try:
            self.media = dict(sorted(self.media.items(), key=lambda x: int(x[0].split('_')[-1].split('.')[0])))
        except Exception as e:
            logging.exception('Names not compatible with sorting: %s', e)


    def _load_media_folder(self, folder_path):
        if not os.path.exists(folder_path):
            raise ValueError("Path does not exist")

        wav_files = [wav for wav in os.listdir(folder_path) if wav.split('.')[-1] == 'wav']
        for wav in wav_files:
            if wav not in self.media.keys():
                self.media[wav] = Media(os.path.join(folder_path,wav))

        mp4_files = [mp4 for mp4 in os.listdir(folder_path) if mp4.split('.')[-1] == 'mp4']
        for mp4 in mp4_files:
            mp4_waved = '.'.join(mp4.split('.')[:-1]) + '.wav'
            if mp4_waved not in self.media.keys():
                _mp42wav(os.path.join(folder_path,mp4), os.path.join(folder_path,mp4_waved))
                self.media[mp4_waved] = Media(os.path.join(folder_path,mp4_waved))

        vtt_files = [vtt for vtt in os.listdir(folder_path) if vtt.split('.')[-1] == 'vtt']
        for vtt in vtt_files:
            vtt_waved = '.'.join(vtt.split('.')[:-1]) + '.wav'
            if vtt_waved in self.media.keys():
                self.media[vtt_waved].subtitles = os.path.join(folder_path,vtt)
    def __str__(self):
        return "<Dataset named " + self.name + ", with " + str(len(self.media)) + " videos/audios and original subtitles.>"







def _mp42wav(input_path, output_path):
    # Load the MP4 audio file
    audio = AudioFileClip(input_path)

    # Convert and save the audio to WAV format
    audio.write_audiofile(output_path, codec='pcm_s16le', bitrate='160k')

    return output_path
