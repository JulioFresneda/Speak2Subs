import nemo
import os
import sys
from omegaconf import OmegaConf, open_dict
import logging
# IMPORTANTE: Necesarias dependendias -dev de Python. Por ejemplo, python3.10-dev
import nemo.collections.asr as nemo_asr

logging.getLogger('nemo_logger').setLevel(logging.ERROR)


media_volume = "/volume/media"

complete_result = {}
model_name="stt_es_quartznet15x5"

for media in sorted(os.listdir(media_volume)):
    print(media)

    # Load the NeMo asr model using the specified model name or the default if not provided
    nemo_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name=model_name)

    # Retrieve the decoding configuration from the NeMo model and customize it
    decoding_cfg = nemo_model.cfg.decoding
    with open_dict(decoding_cfg):
        # Modify decoding parameters to preserve alignments and compute timestamps
        decoding_cfg.preserve_alignments = True
        decoding_cfg.compute_timestamps = True
        nemo_model.change_decoding_strategy(decoding_cfg)

    # Transcribe the provided media file using the NeMo model
    hypotheses = nemo_model.transcribe([os.path.join(media_volume,media)], return_hypotheses=True)

    # Process the transcription results
    if type(hypotheses) == tuple and len(hypotheses) == 2:
        hypotheses = hypotheses[0]  # Unpack hypotheses if returned as a tuple

    # Extract word timestamps and process them to obtain start and end times for each word
    timestamp_dict = hypotheses[0].timestep
    time_stride = 8 * nemo_model.cfg.preprocessor.window_stride
    word_timestamps = timestamp_dict['word']

    final_result = {'text':hypotheses[0].text, 'timestamps':word_timestamps}
    final_result['segment_name'] = media

    complete_result[media] = final_result

# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()