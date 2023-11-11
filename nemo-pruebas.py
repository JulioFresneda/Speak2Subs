import nemo
import os

import nemo.collections.asr as nemo_asr
listasr = nemo_asr.models.EncDecCTCModel.list_available_models()
#print(listasr)


asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="stt_es_quartznet15x5")

files = ['audios/carmen.wav']
for fname, transcription in zip(files, asr_model.transcribe(paths2audio_files=files)):
  print(f"Audio in {fname} was recognized as: {transcription}")

