import copy

def _local_to_original(local_ts, vad_ts, last_global_end = 0):
    original = copy.deepcopy(local_ts)

    for local in original:
        silence = 0
        speech = 0
        last_end = 0
        end_speech = 0

        for vts in vad_ts:
            end_speech += round(vts['end'] - vts['start'], 3)
            silence += round(vts['start'] - last_end, 3)
            last_end = vts['end']
            done = False
            if speech <= local['start'] <= end_speech:
                local['start'] = round(local['start'] + silence + last_global_end, 3)
                local['end'] = round(local['end'] + silence + last_global_end, 3)
                done = True
            if done:
                break
            speech = end_speech

    return original


class Subtitle:
    def __init__(self, text, local_word_timestamps, local_sentences_timestamps, vad_timestamps, last_global_end = 0):
        self.text = text
        self.local_word_timestamps = local_word_timestamps
        self.local_sentences_timestamps = local_sentences_timestamps

        if local_word_timestamps is not None:
            self.original_word_timestamps = _local_to_original(self.local_word_timestamps, vad_timestamps, last_global_end)
        else:
            self.original_word_timestamps = None

        if local_sentences_timestamps is not None:
            self.original_sentences_timestamps = _local_to_original(self.local_sentences_timestamps,
                                                                    vad_timestamps, last_global_end)
        else:
            self.original_sentences_timestamps = None

        self.last_global_end = self.original_word_timestamps[-1]['end']

    def __str__(self):
        return self.text





