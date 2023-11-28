import copy
import os
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

        if(len(self.tokens) > 0):
            self.start = self.tokens[0].start
            self.end = self.tokens[-1].end
        else:
            self.start = 0
            self.end = 0

    def add_token(self, token):
        if(len(self.tokens) == 0):
            self.start = token.start
        self.tokens.append(token)
        self.text += token.text
        self.end = token.end

    def join_subtitle(self, subtitle):
        self.end = subtitle.end
        self.tokens += subtitle.tokens
        self.text += subtitle.text

    @staticmethod
    def merge_subtitles(subtitles: list):
        sub = Subtitle()
        for s in subtitles:
            sub.join_subtitle(s)
        return sub


    def __str__(self):
        return self.text



    def to_vtt(self, template_path = None):
        if(template_path is not None):
            self._to_vtt_based_on_template(template_path)



    def _to_vtt_based_on_template(self, template_path):
        template_ts = self._load_template(template_path)
        predicted_ts_format = []
        for template_sub in template_ts:
            pred_sub = ""
            for token in self.tokens:
                added = False
                if (template_sub['start'] <= token.start <= template_sub['end']):
                    pred_sub += token.text
                    added = True
                #if(not added and template_sub['start'] <= token.end <= template_sub['end']):
                #    pred_sub += token.text

            predicted_ts_format.append({'start':template_sub['start'], 'end':template_sub['end'], 'text':pred_sub})

        name = os.path.basename(template_path).split('.')[0] + "_PRED_" + ".vtt"
        export_path = os.path.join(os.path.dirname(template_path), name)
        self._export_ts_to_vtt(predicted_ts_format, export_path)


    def _export_ts_to_vtt(self, timestamps, export_path):
        if(os.path.exists(export_path)):
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


    def _load_template(self, template_path):

        subtitles_with_timestamps = []
        with open(template_path, 'r') as file:
            lines = file.readlines()

            for line in lines:
                line = line.rstrip('\r\n')
                if(line == 'WEBVTT'):
                    break
                elif(line == ''):
                    break
                elif('-->' in line):
                    ts = self._load_subs_timestamps(line)
                else:
                    try:
                        ts['text'] += line
                    except:
                        ts['text'] = line

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








