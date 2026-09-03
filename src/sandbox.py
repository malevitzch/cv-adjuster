from pathlib import Path

import docker
from docker.models.containers import Container

DOCKERFILE_DIR = Path(__file__).resolve().parents[1]
DOCKERFILE_NAME = "Dockerfile.sandbox"


class Sandbox:
    name: str
    _client: docker.DockerClient
    _container: Container | None

    # TODO: use __enter__ __exit__ RAII
    def __init__(self, name: str = "agent_sandbox_container", verbose: bool = True):
        self.name = name
        # TODO: catch docker crashes
        self._client = docker.from_env()
        self._container = None

        # TODO: do I want image, logs? What do I do with them
        image, logs = self._client.images.build(
            path=str(DOCKERFILE_DIR),
            dockerfile=DOCKERFILE_NAME,
            tag="agent-sandbox:latest",
        )
        if verbose:
            print("Built image:", image.tags[0])

        if verbose:
            print("Setting up sandbox container...")
        self._container = self._client.containers.run(
            "agent-sandbox:latest",
            command="sleep infinity",
            detach=True,
            name=self.name,
        )
        if verbose:
            print("Sandbox container has been set up")
