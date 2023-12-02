import torch
import os
from pydub import AudioSegment

from Speak2Subs import media


class VAD:
    def __init__(self, my_media, max_speech_duration=float('inf'), use_vad=True, segment=True, sentences=False):
        self.media = my_media
        self.max_speech_duration = max_speech_duration
        self.use_vad = use_vad
        self.segment = segment
        self.sentences = sentences

        if not self.segment:
            self.max_speech_duration = float('inf')

    def apply_vad(self):
        self.sampling_rate = 16000

        self._apply_model()
        self._load_segments()
        self._group_segments()
        self._save_segments_to_file()

    def _apply_model(self):
        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                      model='silero_vad',
                                      force_reload=False,
                                      onnx=False,
                                      verbose=False)

        (get_speech_timestamps,
         self.save_audio,
         read_audio,
         VADIterator,
         self.collect_chunks) = utils

        self.wav = read_audio(self.media.path, sampling_rate=self.sampling_rate)
        # get speech timestamps from full audio file

        if (self.use_vad):
            print(" ---> Voice Activity Detection - KO <--- ", end='\r', flush=True)
            self.speech_timestamps = get_speech_timestamps(self.wav, model, sampling_rate=self.sampling_rate,
                                                   max_speech_duration_s=self.max_speech_duration,
                                                   return_seconds=False)
            print(" ---> Voice Activity Detection - OK <--- ")


        else:
            print(" ---> Voice Activity Detection - NO <--- ")
            audio_len = self.wav.shape[0]
            if(self.segment and self.max_speech_duration <= audio_len):
                print(" --->             Segmentation - KO <--- ", end='\r', flush=True)
                self.speech_timestamps = []
                for i in range(0, int(audio_len/self.max_speech_duration)+1, self.sampling_rate):
                    self.speech_timestamps.append({'start':int(i*self.max_speech_duration), 'end':int((i+self.sampling_rate)*self.max_speech_duration)})
                self.speech_timestamps[-1]['end'] = audio_len
                print(" --->             Segmentation - OK <--- ")


            else:
                print(" --->             Segmentation - NO <--- ")
                self.speech_timestamps = [{'start':0, 'end':audio_len}]


    def _load_segments(self):
        segments = []
        for ts in self.speech_timestamps:
            segments.append(media.Segment(ts['start'] / self.sampling_rate, ts['end'] / self.sampling_rate, ts))
        self.segments = segments

    def _group_segments(self):
        result = []
        self.segment_groups = []
        if(not self.sentences):
            print(" --->           Group segments - KO <--- ", end='\r', flush=True)
            current_list = []


            for segment in self.segments:
                duration_so_far = sum([sg.end - sg.start for sg in current_list])
                segment_duration = segment.end - segment.start

                if duration_so_far + segment_duration <= self.max_speech_duration:
                    current_list.append(segment)
                else:
                    result.append(current_list)
                    current_list = [segment]

            if current_list:
                result.append(current_list)
            print(" --->           Group segments - OK <--- ")
        else:
            print(" --->           Group segments - NO <--- ")
            for seg in self.segments:
                result.append([seg])

        self.segment_groups_folder = os.path.join(self.media.folder, "segment_groups")
        if (not os.path.exists(self.segment_groups_folder)):
            os.mkdir(self.segment_groups_folder)

        for i, r in enumerate(result, start=0):
            self.segment_groups.append(self._group_to_media_group(r, i))
        self.media.segments_groups = self.segment_groups

    def _group_to_media_group(self, group, index):
        generated_path = os.path.join(self.segment_groups_folder,
                                      self.media.name.split('.')[0] + "_segment_" + str(index) + ".wav")
        return media.SegmentGroup(group, generated_path)

    def _save_segments_to_file(self):
        for i, st in enumerate(self.segment_groups, start=0):
            print(" --->           Saving audios - " + str(i) + "/" + str(len(self.segment_groups)) + " <--- ", end='\r', flush=True)
            ts_list = []
            for seg in st:
                ts_list.append(seg.ts_dict)
            self.save_audio(st.path, self.collect_chunks(ts_list, self.wav), sampling_rate=16000)

    def _collect_chunks_with_silence(self, tss,
                       wav: torch.Tensor):
        chunks = []
        five_seconds_length = int(self.sampling_rate * 3)
        first_5_seconds_tensor = wav[:five_seconds_length]
        silence_tensor = torch.zeros_like(first_5_seconds_tensor)
        for i in tss:
            wav_with_sil = wav[i['start']: i['end']]
            result_tensor = torch.cat([wav_with_sil, silence_tensor])

            chunks.append(result_tensor)
        return torch.cat(chunks)
