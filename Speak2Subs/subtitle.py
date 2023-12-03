import copy
import os
from Speak2Subs import post_processing
from Speak2Subs.evaluate import eval_une_4_3, eval_une_4_6, eval_une_5_1

class Token:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return self.text


class Subtitle:
    def __init__(self):
        self.tokens = []
        self.text = ""

        if len(self.tokens) > 0:
            self.start = self.tokens[0].start
            self.end = self.tokens[-1].end
        else:
            self.start = 0
            self.end = 0

    def add_token(self, token):
        if len(self.tokens) == 0:
            self.start = token.start
        self.tokens.append(token)
        self.text += token.text
        self.end = token.end

    def join_subtitle(self, subtitle):
        try:
            self.end = subtitle.end
            self.tokens += subtitle.tokens
            self.text += subtitle.text
        except:
            print(subtitle)

    @staticmethod
    def merge_subtitles(subtitles: list):
        sub = Subtitle()
        for s in subtitles:
            sub.join_subtitle(s)
        return sub

    def __str__(self):
        return self.text

    def to_vtt(self, my_media, asr_value, export_path, use_template):
        if my_media.original_subtitles_path is not None and use_template:
            self._to_vtt_based_on_template(my_media, asr_value, export_path)
        else:
            self._to_vtt_blind(my_media, asr_value, export_path)

    def _to_vtt_blind(self, my_media, asr_value, export_path):
        predicted_ts_format = []
        subtitle = ""
        last_end = 0
        for i, token in enumerate(self.tokens, start=0):
            if subtitle == "":
                start = token.start

            if eval_une_4_6(subtitle + token.text) or eval_une_4_3(subtitle + "\n newline"):
                if eval_une_4_6(subtitle + token.text):
                    subtitle = subtitle + token.text
                elif eval_une_4_3(subtitle + "\n newline"):
                    subtitle += "\n" + token.text

                if self._end_of_sentence(subtitle):
                    comply, duration_comply = eval_une_5_1(subtitle, token.end - start)
                    if not comply and i < len(self.tokens)-1 and self.tokens[i+1].start - start > duration_comply:
                        token.end = start + duration_comply

                    predicted_ts_format.append({'text': subtitle, 'start': start, 'end': token.end})
                    subtitle = ""
            else:
                predicted_ts_format.append({'text':subtitle, 'start':start, 'end':last_end})
                subtitle = token.text
                start = token.start

                if self._end_of_sentence(subtitle):
                    #if start < last_end and last_end + 0.1 < token.end:
                    #    start = last_end + 0.1
                    comply, duration_comply = eval_une_5_1(subtitle, token.end - start)
                    if not comply and i < len(self.tokens)-1 and self.tokens[i+1].start - start > duration_comply:
                        token.end = start + duration_comply
                    predicted_ts_format.append({'text': subtitle, 'start': start, 'end': token.end})
                    subtitle = ""

            last_end = token.end





        self._to_vtt_complete_export(my_media, asr_value, export_path, predicted_ts_format)

    def _end_of_sentence(self, sentence):
        is_end = False
        is_end = sentence[-1] == ',' or sentence[-1] == '.' or sentence[-1] == ';'
        if len(sentence) > 1:
            is_end = sentence[-2:] == ', ' or sentence[-2:] == '. ' or sentence[-2:] == '; ' or is_end
        return is_end



    def _to_vtt_based_on_template(self, my_media, asr_value, export_path):
        template_ts, _ = load_template(my_media.original_subtitles_path)
        predicted_ts_format = []
        for template_sub in template_ts:
            pred_sub = ""
            for token in self.tokens:
                added = False
                if template_sub['start'] <= token.end <= template_sub['end']:
                    pred_sub += token.text
                    added = True
                # if(not added and template_sub['start'] <= token.end <= template_sub['end']):
                #    pred_sub += token.text

            predicted_ts_format.append({'start': template_sub['start'], 'end': template_sub['end'], 'text': pred_sub})

        self._to_vtt_complete_export(my_media, asr_value, export_path, predicted_ts_format)
    def _to_vtt_complete_export(self, my_media, asr_value, export_path, predicted_ts_format):
        name = os.path.basename(my_media.original_subtitles_path).split('.')[0] + "_PRED_" + ".vtt"
        export_folder = os.path.join(export_path, asr_value + "_VTT")
        if not os.path.exists(export_folder):
            os.mkdir(export_folder)
        file_export_path = os.path.join(export_folder, name)

        # my_media.vtt_subtitles = {'reference':template_ts, 'predicted':predicted_ts_format}
        self._export_ts_to_vtt(predicted_ts_format, file_export_path)
        try:
            my_media.predicted_subtitles_vtt_path[asr_value] = file_export_path
        except:
            my_media.predicted_subtitles_vtt_path = {}
            my_media.predicted_subtitles_vtt_path[asr_value] = file_export_path

    def _export_ts_to_vtt(self, timestamps, export_path):
        if os.path.exists(export_path):
            os.remove(export_path)

        with open(export_path, 'w') as file:
            file.write("WEBVTT\n\n")

            for ts in timestamps:
                ts_line = self.seconds_to_hhmmss(ts['start']) + " --> " + self.seconds_to_hhmmss(ts['end'])
                file.write(ts_line)
                file.write('\n')
                file.write(ts['text'])
                file.write('\n\n')
            file.close()

    def seconds_to_hhmmss(self, totalseconds):
        hours = int(totalseconds // 3600)
        minutes = int((totalseconds % 3600) // 60)
        seconds = totalseconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def load_template(template_path):
    subtitles_with_timestamps = []
    subtitles = []
    with open(template_path, 'r') as file:
        lines = file.readlines()
        last_ts = None
        for line in lines[1:]:
            line = line.rstrip('\n')
            if line is not '':
                if '-->' in line:
                    ts = _load_subs_timestamps(line)
                else:
                    try:
                        ts['text'] += " " + line.replace("- ", "")
                        last_ts = ts
                    except:
                        ts['text'] = line.replace("- ", "")
                        last_ts = ts
            else:
                try:
                    subtitles_with_timestamps.append(ts.copy())
                    subtitles.append(ts.copy()['text'])
                except:
                    pass
        if lines[-1].rstrip('\n') != '':
            subtitles_with_timestamps.append(last_ts)
            subtitles.append(last_ts['text'])

    return subtitles_with_timestamps, subtitles


def _load_subs_timestamps(line):
    start, end = line.split(" --> ")
    start_h, start_m, start_s = map(float, start.split(":"))
    end_h, end_m, end_s = map(float, end.split(":"))

    start_seconds = start_h * 3600 + start_m * 60 + start_s
    end_seconds = end_h * 3600 + end_m * 60 + end_s

    return {
        "start": round(start_seconds, 3),
        "end": round(end_seconds, 3)
    }
