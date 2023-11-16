import speechbrain as sb

from speechbrain.pretrained import EncoderDecoderASR

asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-commonvoice-14-es")
trans = asr_model.transcribe_file('tests/bdias.wav')
print(trans)