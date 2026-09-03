from pathlib import Path

import docker
from docker.models.containers import Container

DOCKERFILE_DIR = Path(__file__).resolve().parents[1]
DOCKERFILE_NAME = "Dockerfile.sandbox"


class Sandbox:
    name: str
    img_tag: str

    _client: docker.DockerClient
    _container: Container | None
    _verbose: bool = False

    # TODO: use __enter__ __exit__ RAII
    def __init__(
        self,
        tag: str = "agent-sandbox:latest",
        name: str = "agent_sandbox_container",
        verbose: bool = True,
    ):
        self.name = name
        self.img_tag = tag
        # TODO: catch docker crashes
        self._client = docker.from_env()
        self._container = None
        self._verbose = verbose

        # TODO: do I want logs? What do I do with them
        image, logs = self._client.images.build(
            path=str(DOCKERFILE_DIR),
            dockerfile=DOCKERFILE_NAME,
            tag=tag,
        )
        if verbose:
            print("Built image:", image.tags[0])

    def __enter__(self):
        if self._verbose:
            print("Setting up sandbox container...")
        self._remove_existing_container()
        self._container = self._client.containers.run(
            self.img_tag,
            command="sleep infinity",
            detach=True,
            name=self.name,
        )
        if self._verbose:
            print("Sandbox container has been set up")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        container = self._container
        if container is None:
            return
        if self._verbose:
            print(f"Stopping sandbox container {self.name}...")
        container.remove(force=True)
        if self._verbose:
            print(f"Sandbox container {self.name} has been removed")

    def _remove_existing_container(self) -> None:
        try:
            container = self._client.containers.get(self.name)
        except docker.errors.NotFound:
            return

        if self._verbose:
            print(f"Removing existing sandbox container {self.name}...")
        container.remove(force=True)

    def run_command(self, command: str) -> str:
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")
        ec, result = self._container.exec_run(command)
        output = result.decode("utf-8")
        return output
