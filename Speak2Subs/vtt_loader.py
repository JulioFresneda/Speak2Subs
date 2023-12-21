
def load_vtt_template(template_path, strip_newlines = True):
    subtitles_with_timestamps = []
    subtitles = []
    with open(template_path, 'r') as file:
        lines = file.readlines()
        last_ts = None
        for line in lines[1:]:

            if strip_newlines or line == '\n' or '-->' in line:
                line = line.rstrip('\n')
            while len(line) > 1 and line[0] == ' ':
                line = line[1:]
            while len(line) > 1 and line[-1] == ' ':
                line = line[:-1]
            if line != '':
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
