import os.path
import random
from moviepy.editor import AudioFileClip
import logging


class Media:
    def __init__(self, path):
        self.path = path
        self.folder = os.path.dirname(os.path.abspath(path))
        self.name = os.path.basename(path)
        self.original_subtitles_path = None
        self.segments_groups = []

class SegmentGroup:
    def __init__(self, segments, path):
        self.segments = segments
        self.start = round(self.segments[0].start,3)
        self.group_duration = 0.0
        for sg in segments:
            self.group_duration += sg.end - sg.start
        self.group_duration = round(self.group_duration, 3)

        self.path = path
        self.folder = os.path.dirname(os.path.abspath(path))
        self.name = os.path.basename(path)



    def __str__(self):
        return "<" + self.name + ". Has " + str(len(self.segments)) + ", total duration of " + str(self.group_duration) + " (without silences).>"

    def __iter__(self):
        return iter(self.segments)




class Segment:
    def __init__(self, start_ts, end_ts, timestamps):
        self.start = round(start_ts, 3)
        self.end = round(end_ts, 3)
        self.predicted_subtitle = None
        self.ts_dict = timestamps

    def __str__(self):
        return "<Segment. Starts at " + str(self.start) + ", ends at " + str(self.end) + ", duration of " + str(round(self.end-self.start),3) + ".>"



class Dataset:
    def __init__(self, folder_path, name=None):
        if (name != None):
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
                self.media[wav] = Media(os.path.join(folder_path, wav))

        mp4_files = [mp4 for mp4 in os.listdir(folder_path) if mp4.split('.')[-1] == 'mp4']
        for mp4 in mp4_files:
            mp4_waved = '.'.join(mp4.split('.')[:-1]) + '.wav'
            if mp4_waved not in self.media.keys():
                _mp42wav(os.path.join(folder_path, mp4), os.path.join(folder_path, mp4_waved))
                self.media[mp4_waved] = Media(os.path.join(folder_path, mp4_waved))

        vtt_files = [vtt for vtt in os.listdir(folder_path) if vtt.split('.')[-1] == 'vtt']
        for vtt in vtt_files:
            vtt_waved = '.'.join(vtt.split('.')[:-1]) + '.wav'
            if vtt_waved in self.media.keys():
                self.media[vtt_waved].original_subtitles_path = os.path.join(folder_path, vtt)

    def __str__(self):
        return "<Dataset named " + self.name + ", with " + str(
            len(self.media)) + " videos/audios and original subtitles.>"


def _mp42wav(input_path, output_path):
    # Load the MP4 audio file
    audio = AudioFileClip(input_path)

    # Convert and save the audio to WAV format
    audio.write_audiofile(output_path, codec='pcm_s16le', bitrate='160k')

    return output_path
