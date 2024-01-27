# cli.py
import argparse
from Speak2Subs import speak2subs
def main():
    parser = argparse.ArgumentParser(description='Let\'s sub that media!')
    # Add command-line arguments here

    parser.add_argument('--evaluate', action='store_true', help='Evaluate mode')
    parser.add_argument('-mp', '--media_path', type=str, help='Path of the folder (or file) with the .mp4/.wav files (and .vtt if you want)')
    parser.add_argument('-ep', '--export_folder', type=str, help='Path of the folder where you want the results exported')
    parser.add_argument('--asr', type=str, default='whisperx', help='ASR model to use. Can be: whisper, whisperx, nemo, seamless, vosk.')
    parser.add_argument('--no_vad', action='store_true', help='VAD used by default. You can disable it')
    parser.add_argument('--no_segment', action='store_true', help='s2s segments the audio by default. You can disable it, but it is not assured than some ASR models will work')
    parser.add_argument('--no_segment_group', action='store_true', help='Segment into sentences, without grouping')
    parser.add_argument('--max_speech_duration', type=int, default=30, help='Max speech duration for each segment group')
    parser.add_argument('--use_vtt_templates', action='store_true', help='You can use the original VTT files as template for the new ones.')
    parser.add_argument('--reduce_noise', action='store_false', help='If the audio has some noise, maybe this helps.')
    parser.add_argument('--dataset_name', type=str, default=None, help='Set dataset name.')
    parser.add_argument('--ref_vtt_path', type=str, default=None, help='Evaluate mode: Reference VTT path.')
    parser.add_argument('--pred_vtt_path', type=str, default=None, help='Evaluate mode: Predicted VTT path.')

    args = parser.parse_args()

    if ", " in args.asr:
        asrlist = args.asr.split(", ")
    else:
        asrlist = args.asr

    if not args.evaluate:
        speak2subs.transcript(args.media_path,
                              export_path=args.export_folder,
                              asr=asrlist,
                              use_vad=not args.no_vad,
                              segment=not args.no_segment,
                              group_segments=not args.no_segment_group,
                              max_speech_duration=args.max_speech_duration,
                              use_vtt_template=args.use_vtt_templates,
                              reduce_noise=args.reduce_noise)
    else:
        if args.ref_vtt_path is None or args.pred_vtt_path is None:
            speak2subs.evaluateFolder(args.media_path, args.export_folder, args.dataset_name)
        else:
            speak2subs.evaluatePair(args.ref_vtt_path, args.pred_vtt_path)




if __name__ == '__main__':
    main()
