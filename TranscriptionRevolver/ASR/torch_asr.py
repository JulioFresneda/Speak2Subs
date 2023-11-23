import torch
import torchaudio
import os

print(torch.__version__)
print(torchaudio.__version__)

# https://pytorch.org/audio/stable/tutorials/asr_inference_with_ctc_decoder_tutorial.html
class GreedyCTCDecoder(torch.nn.Module):
    def __init__(self, labels, blank=0):
        super().__init__()
        self.labels = labels
        self.blank = blank

    def forward(self, emission: torch.Tensor) -> str:
        """Given a sequence emission over labels, get the best path string
        Args:
          emission (Tensor): Logit tensors. Shape `[num_seq, num_label]`.

        Returns:
          str: The resulting transcript
        """
        indices = torch.argmax(emission, dim=-1)  # [num_seq,]
        indices = torch.unique_consecutive(indices, dim=-1)
        indices = [i for i in indices if i != self.blank]
        return "".join([self.labels[i] for i in indices])




from torchaudio.models.decoder import ctc_decoder
torch.random.manual_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

bundle = torchaudio.pipelines.WAV2VEC2_ASR_LARGE_960H
model = bundle.get_model().to(device)

media_volume = "/home/juliofgx/PycharmProjects/TranscriptionRevolver/host_volume/media"
complete_result = {}

for media in sorted(os.listdir(media_volume)):
    waveform, sample_rate = torchaudio.load(os.path.join(media_volume,media))
    waveform = waveform.to(device)

    if sample_rate != bundle.sample_rate:
        waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)

    with torch.inference_mode():
        features, _ = model.extract_features(waveform)

    with torch.inference_mode():
        emission, _ = model(waveform)

    decoder = GreedyCTCDecoder(labels=bundle.get_labels())
    transcript = decoder(emission[0])










