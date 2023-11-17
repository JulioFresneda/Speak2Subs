import os.path
import random

class Dataset:
    def __init__(self, dir_path, name = None, urls=[]):
        self.name = name
        self.videos_and_original_subs = {}
        self._load_paths(dir_path, urls)

    def get(self, name = None, index = None, get_random = False):
        if(name != None):
            return self.videos_and_original_subs[name]['video'], self.videos_and_original_subs[name]['original_subtitle']
        elif(index != None):
            i = self.videos_and_original_subs.keys()[index]
        elif(get_random):
            i = random.randint(0,len(self.videos_and_original_subs))
        return self.videos_and_original_subs[i]['video'], self.videos_and_original_subs[i]['original_subtitle']

    def getVideos(self):
        v = []
        for key in self.videos_and_original_subs.keys():
            v.append(self.videos_and_original_subs[key]['video'])
        return v.copy()

    def _load_paths(self, dir_path, urls):
        if (urls == []):
            if (os.path.exists(dir_path)):
                videos = []
                for filename in os.listdir(dir_path):
                    filepath = os.path.join(dir_path, filename)
                    if os.path.isfile(filepath):
                        name, filetype = filename.split('.')
                        if (name) not in self.videos_and_original_subs.keys():
                            self.videos_and_original_subs[name] = {'video': "", 'original_subtitle': ""}
                        if (filetype == 'vtt'):
                            self.videos_and_original_subs[name]['original_subtitle'] = filepath
                        else:
                            self.videos_and_original_subs[name]['video'] = filepath

    def __str__(self):
        return "<Dataset named " + self.name + ", with " + str(len(self.videos_and_original_subs)) + " videos/audios and original subtitles.>"


class DatasetLoader:
    def __init__(self, datasets_path):
        self.datasets_path = os.path.abspath(datasets_path)
        self.datasets = {}
        for ds in os.listdir(self.datasets_path):
            self.datasets[ds] = Dataset(os.path.join(self.datasets_path, ds), ds)

    def get(self, name):
        return self.datasets.copy()[name]

    def getAll(self):
        return self.datasets.copy()

    def getRandom(self):
        randomkey = random.choice(list(self.datasets.keys()))
        return self.datasets.copy()[randomkey]
