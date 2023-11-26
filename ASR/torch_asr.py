import torch
import torchaudio
import os

from torchaudio.pipelines import Wav2Vec2Processor, wav2vec2_tiny
from torchaudio.models import Wav2Vec2ForCTC

print(torch.__version__)
print(torchaudio.__version__)

# https://pytorch.org/audio/main/generated/torchaudio.pipelines.Wav2Vec2FABundle.html#torchaudio.pipelines.Wav2Vec2FABundle
# https://pytorch.org/audio/main/tutorials/ctc_forced_alignment_api_tutorial.html
# https://pytorch.org/audio/main/tutorials/forced_alignment_tutorial.html
# https://pytorch.org/audio/stable/tutorials/asr_inference_with_ctc_decoder_tutorial.html



from torchaudio.models.decoder import ctc_decoder
torch.random.manual_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

media_volume = "/home/juliofgx/PycharmProjects/Speak2Subs/host_volume/media"
complete_result = {}

for media in sorted(os.listdir(media_volume)):
    audio_input, sr = torchaudio.load(os.path.join(media_volume,media))

    # Preprocess the audio input
    inputs = processor(audio_input, sampling_rate=sr, return_tensors="pt", padding=True)

    # Perform transcription
    with torch.no_grad():
        logits = model(inputs.input_values).logits

        # Decode the logits to text
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]

    # Print the transcription
    print("Transcription:", transcription)













