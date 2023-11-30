from . import media, subtitle
import jiwer


# https://github.com/jitsi/jiwer
class Evaluator:
    def __init__(self, reference_vtt_file, predicted_vtt_file):
        _, reference = subtitle.load_template(reference_vtt_file)
        _, predicted = subtitle.load_template(predicted_vtt_file)

        wer = jiwer.wer(reference=reference, hypothesis=predicted)
        mer = jiwer.mer(reference=reference, hypothesis=predicted)
        wil = jiwer.wil(reference=reference, hypothesis=predicted)

        output = jiwer.process_words(reference, predicted)
        print(jiwer.visualize_alignment(output))
