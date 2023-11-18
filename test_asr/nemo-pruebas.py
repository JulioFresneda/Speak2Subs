import nemo
import os

import nemo.collections.asr as nemo_asr
listasr = nemo_asr.models.EncDecCTCModel.list_available_models()
#print(listasr)


asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="stt_es_quartznet15x5")

from omegaconf import OmegaConf, open_dict
decoding_cfg = asr_model.cfg.decoding
with open_dict(decoding_cfg):
    decoding_cfg.preserve_alignments = True
    decoding_cfg.compute_timestamps = True
asr_model.change_decoding_strategy(decoding_cfg)

hypotheses = asr_model.transcribe(["../datasets/mda/VAD/segments/mda_1_VAD_VAD_segment_0.wav"], return_hypotheses=True)
if type(hypotheses) == tuple and len(hypotheses) == 2:
    hypotheses = hypotheses[0]
timestamp_dict = hypotheses[0].timestep

time_stride = 8 * asr_model.cfg.preprocessor.window_stride
word_timestamps = timestamp_dict['word']
for stamp in word_timestamps:
    start = stamp['start_offset'] * time_stride
    end = stamp['end_offset'] * time_stride
    word = stamp['char'] if 'char' in stamp else stamp['word']
    print(f"Time : {start:0.2f} - {end:0.2f} - {word}")

