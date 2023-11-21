import docker
import ast, os, io, tarfile
class ContainerManager:
    def __init__(self, ASR, host_volume_path, container_volume_path = '/media'):
        self.client = docker.from_env()
        self.host_volume_path = host_volume_path
        self.container_volume_path = container_volume_path
        self.ASR = ASR
        self._initialize_containers()

    def _initialize_containers(self):
        self.containers = {}
        for asr in self.ASR:
            image_name = "juliofresneda/tr_" + asr.value + "_asr:latest"
            container_name = asr.value + "_container"
            self.containers[asr.value] = self._initialize_container(image_name, container_name)


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




    def execute_in_container(self, asr, media_names):

        container = self.containers[asr.value]


        # Specify the local folder and its path inside the container
        container_path = self.container_volume_path  # Adjust as needed



        exec_command = f"ls {container_path}"
        exec_result = container.exec_run(exec_command)

        exec_command = ["python", "/workdir/transcript.py"] + media_names
        exec_result = container.exec_run(exec_command)

        list_of_dicts_string = exec_result.decode('utf-8')  # Use the appropriate encoding
        list_of_dicts_string = ast.literal_eval(list_of_dicts_string)

        exec_command = f"rm -r {container_path}/*"
        exec_result = container.exec_run(exec_command)

        return list_of_dicts_string  # Print or process the logs as needed

    def _remove_container_if_exists(self, container_name):
        # Check if a container with the given name exists
        try:
            existing_container = self.client.containers.get(container_name)
            # If the container exists, stop and remove it
            existing_container.stop()
            existing_container.remove()
            print(f"Container '{container_name}' exists, but now it is stopped and removed.")
        except docker.errors.NotFound:
            pass