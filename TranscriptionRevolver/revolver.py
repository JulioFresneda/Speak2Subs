from enum import Enum
import subprocess  # Importing the subprocess module to execute shell commands
import os  # Importing the os module for operating system-related functionality
import docker
import json
import ast

class ASRNames(Enum):
    WHISPERX = 'whisperx'
    NEMO = 'nemo'
    VOSK = 'vosk'
    SPEECHBRAIN = 'speechbrain'
    TORCH = 'torch'
    WHISPER = 'whisper'

class Revolver:
    def __init__(self, ASR):
        if isinstance(ASR, str) and ASR == 'all':
            self.asr_to_apply = list(ASRNames)
        elif isinstance(ASR, list) and all(item.lower() in ASRNames for item in ASR):
            self.asr_to_apply = ASR.copy()


    def apply_asr(self, dataset, original, vad, vad_segments):
        for asr in self.asr_to_apply:
            if(original):
                for media in dataset.media:
                    self.shot(asr, media.original_media_path)
            elif(vad):
                for media in dataset.media:
                    self.shot(asr, media.vad_media_path)
            elif(vad_segments):
                for media in dataset.media:
                    media_names = []
                    for seg in media.vad_segments_paths:
                        media_names.append(os.path.basename(seg))
                    self.shot(asr, media.vad_segments_folder, media_names)

                # for media in dataset.media:
                #    for segment in media.vad_segments_paths:
                #        self.shot(asr, segment)




    def shot(self, asr, volume_path, media_names):
        if(asr == ASRNames.NEMO):
            #text, timestamps = nemo_asr.apply_nemo(media_path)
            #print(text)
            pass
        elif(asr == ASRNames.WHISPER):
            #text, timestamps = whisper_asr.apply_whisper(media_path)
            #print(text)
            pass
        elif(asr == ASRNames.VOSK):
            result = run_container_with_volume("juliofresneda/tr_vosk_asr:latest", volume_path, media_names, "/vosk/vosk_asr.py")







            # Path to the virtual environment for Vosk
            #vosk_venv_path = os.path.abspath("./TranscriptionRevolver/ASR/vosk_venv")

            # Executing Module A script within its virtual environment and capturing the output
            #result = execute_module_script(os.path.abspath("./TranscriptionRevolver/ASR/vosk_asr.py"), vosk_venv_path, script_args)
            #print("Module A Result:", result)



def run_container_with_volume(image_name, volume_path, media_names, script):
    client = docker.from_env()

    # Specify the local folder and its path inside the container
    container_folder_path = '/vosk/media'  # Adjust as needed

    # Mount the folder when running the container
    volumes = {volume_path: {'bind': container_folder_path, 'mode': 'rw'}}

    # Join the list into a single string with space-separated elements
    strings_argument = ' '.join(media_names)

    # Run the Docker container with the mounted folder
    container = client.containers.run(
        image_name,
        command=strings_argument,
        volumes=volumes,
        detach=False
    )

    list_of_dicts_string = container.decode('utf-8') # Use the appropriate encoding
    list_of_dicts_string = ast.literal_eval(list_of_dicts_string)


    return list_of_dicts_string  # Print or process the logs as needed




""" # Using containers now
def activate_environment(env_path):
    # Function to generate the command to activate a virtual environment
    activate_script = "activate"

    # Constructing the path to the activation script in the virtual environment
    activate_path = os.path.join(env_path, "Scripts", activate_script) \
        if os.name == "nt" else os.path.join(env_path, "bin", activate_script)

    # Constructing the command to activate the virtual environment based on the OS
    activate_cmd = f"source {activate_path}" if os.name != "nt" else f"{activate_path}"
    return activate_cmd  # Returning the activation command


def execute_module_script(script_path, env_path, *args):
    # Function to execute a Python script within a specific virtual environment

    activate_cmd = activate_environment(env_path)
    if os.access(env_path, os.X_OK):
        print("Venv is executable")
    else:
        os.chmod(env_path, 0o777)
        if os.access(env_path, os.X_OK):
            print("Venv is executable")
    arg_str = ' '.join(args)  # Joining the passed arguments into a single string

    cmd = f"{activate_cmd} && python {script_path} {arg_str}"
    if os.access(script_path, os.X_OK):
        print("script is executable")
    else:
        os.chmod(script_path, 0o777)
        if os.access(script_path, os.X_OK):
            print("script is executable")
    # Running the command in a subprocess and capturing its output
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, executable='/bin/bash')
    return result.stdout  # Returning the output from the executed script
"""

















