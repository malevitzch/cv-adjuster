import tarfile
from io import BytesIO
from os import PathLike
from pathlib import Path, PurePosixPath

import docker
from docker.errors import NotFound
from docker.models.containers import Container

DOCKERFILE_DIR = Path(__file__).resolve().parents[1]
DOCKERFILE_NAME = "Dockerfile.sandbox"
CONTAINER_WORKDIR = PurePosixPath("/workspace")


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
        except NotFound:
            return

        if self._verbose:
            print(f"Removing existing sandbox container {self.name}...")
        container.remove(force=True)

    def run_command(self, command: str) -> str:
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")
        result = self._container.exec_run(command)
        output = result.output.decode("utf-8")
        return output

    def copy_to(
        self, host_src: str | PathLike[str], container_dest: str | PathLike[str]
    ) -> None:
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        source = Path(host_src)
        destination = PurePosixPath(container_dest)
        if not destination.is_absolute():
            destination = CONTAINER_WORKDIR / destination

        archive = BytesIO()
        with tarfile.open(fileobj=archive, mode="w") as tar:
            tar.add(source, arcname=source.name)

        self._container.put_archive(str(destination), archive.getvalue())

    def copy_from(
        self, container_src: str | PathLike[str], host_dest: str | PathLike[str]
    ) -> None:
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        source = PurePosixPath(container_src)
        if not source.is_absolute():
            source = CONTAINER_WORKDIR / source

        destination = Path(host_dest)
        destination.mkdir(parents=True, exist_ok=True)
        archive_stream, _ = self._container.get_archive(str(source))
        archive = BytesIO(b"".join(archive_stream))

        with tarfile.open(fileobj=archive, mode="r:") as tar:
            destination_root = destination.resolve()
            members = tar.getmembers()
            for member in members:
                member_path = (destination / member.name).resolve()
                if not member_path.is_relative_to(destination_root):
                    raise ValueError(
                        f"Archive member escapes destination: {member.name}"
                    )
                if not (member.isfile() or member.isdir()):
                    raise ValueError(f"Unsupported archive member: {member.name}")
            tar.extractall(destination, members=members)
