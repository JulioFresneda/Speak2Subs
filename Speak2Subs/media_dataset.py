import os.path
import random
from moviepy.editor import AudioFileClip

class Dataset:
    def __init__(self, dir_path, name, parent_path, urls=[]):
        self.name = name

        # Always keep order
        self.media = []
        self.media_names = []
        self.dir_path = dir_path
        self.parent_path = parent_path

        self._load_paths(dir_path, urls)
        self._order_media()



    def get_original(self, name = None, index = None, get_random = False):
        if(name != None):
            index = self.media_names.index(name)
            return self.media[index]
        elif(index != None):
            i = index
        elif(get_random):
            i = random.randint(0, len(self.media_names))
        return self.media[index]




    def _order_media(self):
        sorted_indices = sorted(range(len(self.media_names)), key=lambda i: self.media_names[i])
        self.media_names = [self.media_names[i] for i in sorted_indices]
        self.media = [self.media[i] for i in sorted_indices]

    def has_vad(self):
        """
        Checks if any media item in the object has a VAD (Voice Activity Detection) version.

        Returns:
        - has_vad (bool): Indicates whether any media item has a VAD version.
        - count (int): Number of media items with VAD versions.
        """
        i = 0  # Initialize a counter to track the number of media items with VAD versions
        for m in self.media:
            if m.vad_media_path is not None:  # Check if the VAD version for a media item exists
                i += 1  # Increment the counter for each media item with a VAD version

        has_vad = i > 0  # Set has_vad to True if any media item has a VAD version, False otherwise
        return has_vad, i  # Return a tuple indicating if any VAD exists and the count of VAD versions found

    def has_vad_segments(self):
        i = 0
        for m in self.media:
            if(m.vad_segments_paths != []):
                i+=1
        hasvad_segments = i > 0
        return hasvad_segments, i
    def _load_paths(self, dir_path, urls):
        if (urls == []):


            if (os.path.exists(dir_path)):
                files = {}
                for filename in os.listdir(dir_path):
                    filepath = os.path.join(dir_path, filename)
                    if os.path.isfile(filepath):
                        name, filetype = filename.split('.')
                        if(name not in files.keys()):
                            files[name] = []

                        if(filetype not in files[name]):
                            files[name].append(filetype)

                for name in files.keys():
                    if(name not in self.media_names):
                        # Condition
                        if('vtt' in files[name]):
                            self.media_names.append(name)
                            vttpath = os.path.join(dir_path, name + '.vtt')

                            if('wav' in files[name]):
                                wavpath = os.path.join(dir_path, name+'.wav')


                            elif('mp4' in files[name]):
                                wavpath = os.path.join(dir_path, name+'.wav')
                                mp4path = os.path.join(dir_path, name+'.mp4')
                                if (not os.path.exists(wavpath)):
                                    _mp42wav(mp4path, wavpath)

                            else:
                                wavpath = ""
                                vttpath = ""

                            self.media.append(Media(wavpath, vttpath, name=name))



    def __str__(self):
        return "<Dataset named " + self.name + ", with " + str(len(self.media_names)) + " videos/audios and original subtitles. VAD: " + str(self.has_vad()) + ". VAD Segments: " + str(self.has_vad_segments()) + ".>"


class Media:
    def __init__(self, original_media_path, original_subtitles_path, name=None):
        self.original_media_path = original_media_path
        self.original_subtitle_path = original_subtitles_path
        self.vad_media_path = None
        self.vad_timestamps = None

        self.vad_segments_paths = []
        self.vad_segments_folder = None
        self.vad_segments_ts = []

        self.name = name

    def add_vad(self, vad_media_path, vad_timestamps):
        self.vad_media_path = vad_media_path
        self.vad_timestamps = vad_timestamps

    def add_vad_segments(self, vad_segments_paths, vad_segments_ts):
        self.vad_segments_paths = vad_segments_paths
        self.vad_segments_folder = os.path.dirname(vad_segments_paths[0])
        self.vad_segments_ts = vad_segments_ts

    def get_media_names(self):
        media_names = {}
        media_names['original'] = os.path.basename(self.original_media_path)
        media_names['VAD'] = os.path.basename(self.vad_media_path)
        media_names['VAD_segments'] = []
        for m in self.vad_segments_paths:
            media_names['VAD_segments'].append(os.path.basename(m))

        return media_names



class DatasetLoader:
    def __init__(self, datasets_path):
        self.datasets_path = os.path.abspath(datasets_path)
        self.datasets = {}
        for ds in os.listdir(self.datasets_path):
            self.datasets[ds] = Dataset(os.path.join(self.datasets_path, ds), ds, os.path.abspath(datasets_path))

    def get(self, name):
        return self.datasets.copy()[name]

    def getAll(self):
        return self.datasets.copy()

    def getRandom(self):
        randomkey = random.choice(list(self.datasets.keys()))
        return self.datasets.copy()[randomkey]



def _mp42wav(input_path, output_path):
    # Load the MP4 audio file
    audio = AudioFileClip(input_path)

    # Convert and save the audio to WAV format
    audio.write_audiofile(output_path, codec='pcm_s16le', bitrate='160k')

    return output_path