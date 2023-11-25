class Subtitle:
    def __init__(self, text, local_word_timestamps, local_sentences_timestamps, vad_timestamps):
        self.text = text
        self.local_word_timestamps = local_word_timestamps
        self.local_sentences_timestamps = local_sentences_timestamps

        if(local_word_timestamps != None):
            self.original_word_timestamps = self._local_to_original(self.local_word_timestamps, vad_timestamps)
        else:
            self.original_word_timestamps = None

        if(local_sentences_timestamps != None):
            self.original_sentences_timestamps = self._local_to_original(self.local_sentences_timestamps, vad_timestamps)
        else:
            self.original_sentences_timestamps = None


    def _local_to_original(self, local_ts, vad_ts):
        original = local_ts.copy()

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
                if(local['start'] >= speech and local['start'] <= end_speech):
                    local['start'] = round(local['start'] + silence,2)
                    local['end'] = round(local['end'] + silence, 2)
                    done = True
                if(done):
                    break
                speech = end_speech



        return original













    def _calculate_speech(self, vad_token, vad_ts):
        speech = 0.0
        for vts in vad_ts:
            if(vts != vad_token):
                speech += vts['end'] - vts['start']
            else:
                return speech
        return speech


    def _calculate_silence(self, token_starts, vad_ts):
        silence = 0.0
        last_end = 0.0
        for vts in vad_ts:
            new_silence = silence + vts['start'] - last_end
            last_end = vts['end']
            if(new_silence > token_starts):
                return silence
            else:
                silence = new_silence
        return silence








    def __str__(self):
        return self.text
