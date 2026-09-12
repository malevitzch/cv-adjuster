import tarfile
from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO
from os import PathLike
from pathlib import Path, PurePosixPath

import docker
from docker.errors import NotFound
from docker.models.containers import Container

DEFAULT_DOCKERFILE_DIR = Path(__file__).resolve().parents[1] / "dockerfiles"
DEFAULT_DOCKERFILE_NAME = "Dockerfile.sandbox"
DEFAULT_DOCKERFILE_PATH = DEFAULT_DOCKERFILE_DIR / DEFAULT_DOCKERFILE_NAME
CONTAINER_WORKDIR = PurePosixPath("/workspace")


class Permissions(StrEnum):
    READ_ONLY = "r"
    READ_WRITE = "rw"


@dataclass
class SandboxDirectory:
    """A directory in the sandbox container."""

    path: PathLike[str] | str
    permissions: Permissions


def read_only_directory(path: PathLike[str]) -> SandboxDirectory:
    return SandboxDirectory(path=path, permissions=Permissions.READ_ONLY)


def read_write_directory(path: PathLike[str]) -> SandboxDirectory:
    return SandboxDirectory(path=path, permissions=Permissions.READ_WRITE)


class Sandbox:
    name: str
    img_tag: str

    _client: docker.DockerClient
    _container: Container | None
    _verbose: bool = False
    _directories: list[SandboxDirectory]

    # TODO: use __enter__ __exit__ RAII
    def __init__(
        self,
        tag: str = "agent-sandbox:latest",
        name: str = "agent_sandbox_container",
        verbose: bool = True,
        directories: list[SandboxDirectory] | None = None,
        dockerfile: Path = DEFAULT_DOCKERFILE_PATH,
    ):
        self.name = name
        self.img_tag = tag
        # TODO: catch docker crashes
        self._client = docker.from_env()
        self._container = None
        self._verbose = verbose
        if directories is None:
            self._directories = []
        else:
            self._directories = directories

        # TODO: do I want logs? What do I do with them
        image, logs = self._client.images.build(
            path=str(dockerfile.parent),
            dockerfile=dockerfile.name,
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

        for sandbox_directory in self._directories:
            self.create_directory(sandbox_directory)

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

    def create_directory(self, sandbox_directory: SandboxDirectory) -> None:
        """Create a container directory with access granted to the ``agent`` group."""
        container_path = self._container_path(sandbox_directory.path)
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        result = self._container.exec_run(
            ["mkdir", "-p", str(container_path)], user="root"
        )
        if result.exit_code != 0:
            output = result.output.decode("utf-8")
            raise RuntimeError(f"Could not create sandbox directory: {output}")

        # Keep root as the owner, but make agent the owning group. The setgid bit
        # makes files and subdirectories created below inherit the agent group.
        result = self._container.exec_run(
            ["chown", "root:agent", str(container_path)], user="root"
        )
        if result.exit_code != 0:
            output = result.output.decode("utf-8")
            raise RuntimeError(f"Could not set sandbox directory group: {output}")

        match sandbox_directory.permissions:
            case Permissions.READ_ONLY:
                mode = "2550"
            case Permissions.READ_WRITE:
                mode = "2770"

        result = self._container.exec_run(
            ["chmod", mode, str(container_path)], user="root"
        )
        if result.exit_code != 0:
            output = result.output.decode("utf-8")
            raise RuntimeError(f"Could not set sandbox directory permissions: {output}")

    def run_command(self, command: str) -> str:
        """Run a shell command inside the sandbox and return its combined output."""
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")
        result = self._container.exec_run(["bash", "-lc", command])
        output = result.output.decode("utf-8")
        return output

    def _make_owned_by_agent(self, container_path: PurePosixPath) -> None:
        """Allow the unprivileged container user to edit uploaded files."""
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        result = self._container.exec_run(
            ["chown", "-R", "agent:agent", str(container_path)], user="root"
        )
        if result.exit_code != 0:
            output = result.output.decode("utf-8")
            raise RuntimeError(f"Could not set sandbox file ownership: {output}")

    def _make_read_only_for_agent(self, container_path: PurePosixPath) -> None:
        """Make uploaded files readable, but not writable, by the ``agent`` group."""
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        result = self._container.exec_run(
            ["chown", "-R", "root:agent", str(container_path)], user="root"
        )
        if result.exit_code != 0:
            output = result.output.decode("utf-8")
            raise RuntimeError(f"Could not set sandbox file group: {output}")

        result = self._container.exec_run(
            ["chmod", "-R", "g+rX,g-w,o-rwx", str(container_path)], user="root"
        )
        if result.exit_code != 0:
            output = result.output.decode("utf-8")
            raise RuntimeError(f"Could not set sandbox file permissions: {output}")

    def _prepare_uploaded_path(self, container_path: PurePosixPath) -> None:
        """Apply the configured permissions after Docker has extracted an archive."""
        for sandbox_directory in self._directories:
            directory_path = self._container_path(sandbox_directory.path)
            if container_path.is_relative_to(directory_path):
                if sandbox_directory.permissions is Permissions.READ_ONLY:
                    self._make_read_only_for_agent(container_path)
                else:
                    self._make_owned_by_agent(container_path)
                return

        self._make_owned_by_agent(container_path)

    def copy_to(
        self, host_src: str | PathLike[str], container_dest: str | PathLike[str]
    ) -> None:
        """Copy a file or directory into a container directory.

        A directory is copied as a directory, including its top-level name.
        """
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        source = Path(host_src)
        if not (source.is_file() or source.is_dir()):
            raise FileNotFoundError(source)

        archive = BytesIO()
        with tarfile.open(fileobj=archive, mode="w") as tar:
            tar.add(source, arcname=source.name)

        self._container.put_archive(
            str(self._container_path(container_dest)), archive.getvalue()
        )
        self._prepare_uploaded_path(self._container_path(container_dest) / source.name)

    def copy_directory_contents_to(
        self, host_src: str | PathLike[str], container_dest: str | PathLike[str]
    ) -> None:
        """Copy all direct contents of a host directory into a container directory."""
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        source = Path(host_src)
        if not source.is_dir():
            raise NotADirectoryError(source)

        archive = BytesIO()
        with tarfile.open(fileobj=archive, mode="w") as tar:
            for child in source.iterdir():
                tar.add(child, arcname=child.name)

        self._container.put_archive(
            str(self._container_path(container_dest)), archive.getvalue()
        )
        self._prepare_uploaded_path(self._container_path(container_dest))

    def copy_from(
        self, container_src: str | PathLike[str], host_dest: str | PathLike[str]
    ) -> None:
        """Copy a file or directory into a host directory.

        A directory is copied as a directory, including its top-level name.
        """
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        archive_stream, _ = self._container.get_archive(
            str(self._container_path(container_src))
        )
        self._extract_archive(archive_stream, Path(host_dest))

    def copy_directory_contents_from(
        self, container_src: str | PathLike[str], host_dest: str | PathLike[str]
    ) -> None:
        """Copy all contents of a container directory into a host directory."""
        if self._container is None:
            raise RuntimeError("Sandbox container is not running")

        source = self._container_path(container_src)
        archive_stream, stat = self._container.get_archive(str(source))
        source_name = PurePosixPath(stat["name"]).name if stat else source.name
        self._extract_archive(archive_stream, Path(host_dest), strip_prefix=source_name)

    @staticmethod
    def _container_path(path: str | PathLike[str]) -> PurePosixPath:
        container_path = PurePosixPath(path)
        if container_path.is_absolute():
            return container_path
        return CONTAINER_WORKDIR / container_path

    @staticmethod
    def _extract_archive(
        archive_stream, destination: Path, strip_prefix: str | None = None
    ) -> None:
        """Safely extract a Docker archive, optionally omitting its root directory."""
        destination.mkdir(parents=True, exist_ok=True)
        archive = BytesIO(b"".join(archive_stream))

        with tarfile.open(fileobj=archive, mode="r:") as tar:
            destination_root = destination.resolve()
            members = tar.getmembers()
            has_root_directory = strip_prefix is not None and any(
                PurePosixPath(member.name) == PurePosixPath(strip_prefix)
                and member.isdir()
                for member in members
            )
            if has_root_directory:
                members = Sandbox._strip_archive_prefix(members, strip_prefix)

            for member in members:
                member_path = (destination / member.name).resolve()
                if not member_path.is_relative_to(destination_root):
                    raise ValueError(
                        f"Archive member escapes destination: {member.name}"
                    )
                if not (member.isfile() or member.isdir()):
                    raise ValueError(f"Unsupported archive member: {member.name}")
            tar.extractall(destination, members=members)

    @staticmethod
    def _strip_archive_prefix(
        members: list[tarfile.TarInfo], prefix: str
    ) -> list[tarfile.TarInfo]:
        stripped_members = []
        prefix_path = PurePosixPath(prefix)
        for member in members:
            member_path = PurePosixPath(member.name)
            if member_path == prefix_path:
                continue
            if member_path.parts[:1] != prefix_path.parts:
                raise ValueError(f"Archive member is outside source: {member.name}")
            member.name = str(PurePosixPath(*member_path.parts[1:]))
            stripped_members.append(member)
        return stripped_members
