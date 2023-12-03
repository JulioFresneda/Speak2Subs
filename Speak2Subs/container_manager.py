import docker
import ast, os, io, tarfile
import time
from Speak2Subs import speak2subs

class ContainerManager:
    def __init__(self, asr, host_volume_path, container_volume_path='/volume'):
        self.client = docker.from_env()
        self.host_volume_path = host_volume_path
        self.container_volume_path = container_volume_path
        self.asr = asr
        self._initialize_containers()

    def _initialize_containers(self):
        print(" ------- Initializing containers")
        self.containers = {}

        for asr in self.asr:
            print(" ------> " + asr.value + " - KO", end='\r', flush=True)
            image_name = speak2subs.ASR.image(asr)
            container_name = asr.value + "_container"
            self.containers[asr.value] = self._initialize_container(image_name, container_name)
            print(" ------> " + asr.value + " - OK")

    def _initialize_container(self, image_name, container_name):

        self._remove_container_if_exists(container_name)

        volume_binding = {
            self.host_volume_path: {
                'bind': self.container_volume_path,
                'mode': 'rw'  # Adjust the mode as needed (rw: read-write, ro: read-only)
            }
        }

        # Run the Docker container with the mounted folder
        container = self.client.containers.run(
            image_name,
            name=container_name,
            volumes=volume_binding,
            detach=True
        )
        return container

    def execute_in_container(self, asr):

        self.container = self.containers[asr.value]

        print(" ------> Running transcription in container - KO", end='\r', flush=True)
        exec_command = ["python", "/workdir/transcript.py"]
        self.container.exec_run(exec_command, detach=True)
        self._check_variable()

        result_path = os.path.join(self.host_volume_path, "result.txt")

        with open(result_path, 'r') as file:
            list_of_dicts_string = file.read()

        if os.path.isfile(result_path):
            os.remove(result_path)

        list_of_dicts_string = ast.literal_eval(list_of_dicts_string)
        return list_of_dicts_string  # Print or process the logs as needed

    def _remove_container_if_exists(self, container_name):
        # Check if a container with the given name exists
        try:
            existing_container = self.client.containers.get(container_name)
            # If the container exists, stop and remove it
            existing_container.stop()
            existing_container.remove()
            #print(f"Container '{container_name}' exists, but now it is stopped and removed.")
        except:
            pass


    def _check_variable(self):
        result_path = os.path.join(self.host_volume_path, "progress.txt")
        string = 0
        while(string != 'DONE'):
            if(os.path.exists(result_path)):
                with open(result_path, 'r') as file:
                    # Write a string to the file
                    string = file.readline()
                    file.close()
                print(" ------> Running transcription in container - " + str(string), end='\r', flush=True)
            time.sleep(2)
