# cli.py
import argparse
from Speak2Subs import speak2subs
def transcript():
    parser = argparse.ArgumentParser(description='Let\'s sub that media!')
    # Add command-line arguments here

    parser.add_argument('-mf', '--media_folder', type=str, help='Path of the folder with the .mp4/.wav files (and .vtt if you want)')
    parser.add_argument('-ep', '--export_folder', type=str, help='Path of the folder where you want the results exported')
    parser.add_argument('--asr', type=str, default='whisperx', help='ASR model to use. Can be: whisper, whisperx, nemo, seamless, vosk.')
    parser.add_argument('--no_vad', action='store_true', help='VAD used by default. You can disable it')
    parser.add_argument('--no_segment', action='store_true', help='s2s segments the audio by default. You can disable it, but it is not assured than some ASR models will work')
    parser.add_argument('--sentences', action='store_false', help='Segment into sentences, without grouping')
    parser.add_argument('--max_speech_duration', type=int, default=30, help='Max speech duration for each segment group')
    parser.add_argument('--use_vtt_templates', action='store_false', help='You can use the original VTT files as template for the new ones.')
    parser.add_argument('--reduce_noise', action='store_false', help='If the audio has some noise, maybe this helps.')

    args = parser.parse_args()

    speak2subs.transcript(args.media_folder,
                          export_path=args.export_folder,
                          asr=args.asr,
                          use_vad=not args.no_vad,
                          segment=not args.no_segment,
                          sentences=args.sentences,
                          max_speech_duration=args.max_speech_duration,
                          use_vtt_template=args.use_vtt_templates,
                          reduce_noise=args.reduce_noise)

if __name__ == '__main__':
    transcript()
