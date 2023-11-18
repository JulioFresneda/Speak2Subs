import nemo
import os
from omegaconf import OmegaConf, open_dict

# IMPORTANTE: Necesarias dependendias -dev de Python. Por ejemplo, python3.10-dev
import nemo.collections.asr as nemo_asr

def list_nemo_models():
    return nemo_asr.models.EncDecCTCModel.list_available_models()


def apply_nemo(media_path, model_name="stt_es_quartznet15x5"):
    """
    Apply NeMo ASR model for transcription and extract word-level timestamps.

    Args:
    - media_path (str): Path to the audio file for transcription.
    - model_name (str, optional): Name of the NeMo ASR model to use for transcription.
                                  Defaults to "stt_es_quartznet15x5".

    Returns:
    - None: Prints word-level timestamps with their corresponding start and end times.
    """

    # Load the NeMo ASR model using the specified model name or the default if not provided
    nemo_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="stt_es_quartznet15x5")

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
    """
    for stamp in word_timestamps:
        # Calculate start and end times for each word based on provided offsets
        start = stamp['start_offset'] * time_stride
        end = stamp['end_offset'] * time_stride
        # Retrieve the word label from the transcription stamp
        word = stamp['char'] if 'char' in stamp else stamp['word']
        # Print out the word with its corresponding start and end times
        print(f"Time : {start:0.2f} - {end:0.2f} - {word}")
        
    """

    return hypotheses[0].text, timestamp_dict
