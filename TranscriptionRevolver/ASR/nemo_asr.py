import nemo
import os
import sys
from omegaconf import OmegaConf, open_dict
import logging
# IMPORTANTE: Necesarias dependendias -dev de Python. Por ejemplo, python3.10-dev
import nemo.collections.asr as nemo_asr

logging.getLogger('nemo_logger').setLevel(logging.ERROR)


media_volume = "/nemo/media"
#media_out_names = sys.argv[1:]
media_out_names = ["mda_1_VAD_segment_0.wav", "mda_1_VAD_segment_1.wav"]

complete_result = []
model_name="stt_es_quartznet15x5"

for media_name in media_out_names:
    media_path = os.path.join(media_volume,media_name)

    # Load the NeMo ASR model using the specified model name or the default if not provided
    nemo_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name=model_name, )

    # Retrieve the decoding configuration from the NeMo model and customize it
    decoding_cfg = nemo_model.cfg.decoding
    with open_dict(decoding_cfg):
        # Modify decoding parameters to preserve alignments and compute timestamps
        decoding_cfg.preserve_alignments = True
        decoding_cfg.compute_timestamps = True
        nemo_model.change_decoding_strategy(decoding_cfg)

    # Transcribe the provided media file using the NeMo model
    hypotheses = nemo_model.transcribe([media_path], return_hypotheses=True)

    # Process the transcription results
    if type(hypotheses) == tuple and len(hypotheses) == 2:
        hypotheses = hypotheses[0]  # Unpack hypotheses if returned as a tuple

    # Extract word timestamps and process them to obtain start and end times for each word
    timestamp_dict = hypotheses[0].timestep
    time_stride = 8 * nemo_model.cfg.preprocessor.window_stride
    word_timestamps = timestamp_dict['word']

    result = {'media_name':media_name, 'text':hypotheses[0].text}
    result['timestamps'] = timestamp_dict
    complete_result.append(result)

sys.stdout.write(str(complete_result))