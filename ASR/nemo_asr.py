import nemo
import os
import sys
from omegaconf import OmegaConf, open_dict

# IMPORTANTE: Necesarias dependendias -dev de Python. Por ejemplo, python3.10-dev
import nemo.collections.asr as nemo_asr

def save_progress(string):
    with open('/volume/progress.txt', 'w') as file:
        # Write a string to the file
        file.write(string)
        file.close()

media_volume = "/volume/media"

complete_result = {}
model_name="stt_es_conformer_ctc_large"

# Load the NeMo asr model using the specified model name or the default if not provided
nemo_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name=model_name)

# Retrieve the decoding configuration from the NeMo model and customize it
decoding_cfg = nemo_model.cfg.decoding
with open_dict(decoding_cfg):
    # Modify decoding parameters to preserve alignments and compute timestamps
    decoding_cfg.preserve_alignments = True
    decoding_cfg.compute_timestamps = True
    nemo_model.change_decoding_strategy(decoding_cfg)

for i, media in enumerate(sorted(os.listdir(media_volume)), start=0):
    print(media)

    # Transcribe the provided media file using the NeMo model
    hypotheses = nemo_model.transcribe([os.path.join(media_volume,media)], return_hypotheses=True)
    print(hypotheses)
    # Process the transcription results
    if type(hypotheses) == tuple and len(hypotheses) == 2:
        hypotheses = hypotheses[0]  # Unpack hypotheses if returned as a tuple

    # Extract word timestamps and process them to obtain start and end times for each word
    timestamp_dict = hypotheses[0].timestep
    time_stride = 4 * nemo_model.cfg.preprocessor.window_stride
    word_timestamps = timestamp_dict['word']

    for word in word_timestamps:
        word['start'] = word.pop('start_offset') * time_stride
        word['end'] = word.pop('end_offset') * time_stride
        word['token'] = word.pop('word')

    final_result = {'text':hypotheses[0].text, 'words_ts':word_timestamps}

    complete_result[media] = final_result

    save_progress(str(i) + '/' + str(len(os.listdir(media_volume))))



# Open a file in write mode ('w')
with open('/volume/result.txt', 'w') as file:
    # Write a string to the file
    file.write(str(complete_result))
    file.close()

save_progress("DONE")