import contextlib
import functools
import hashlib
import io
import logging
import os
import platform
import shutil
import tarfile
import tempfile
import typing
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import IO, ClassVar

import anyio
import anyio.to_thread
import httpx
import platformdirs

import dagger

from ._version import CLI_VERSION
from .progress import Progress

logger = logging.getLogger(__name__)

asyncify = anyio.to_thread.run_sync


class Platform(typing.NamedTuple):
    os: str
    arch: str


def get_platform() -> Platform:
    normalized_arch = {
        "x86_64": "amd64",
        "aarch64": "arm64",
    }
    uname = platform.uname()
    os_name = uname.system.lower()
    arch = uname.machine.lower()
    arch = normalized_arch.get(arch, arch)
    return Platform(os_name, arch)


class TempFile(contextlib.AbstractContextManager):
    """Create a temporary file that only deletes on error."""

    def __init__(self, prefix: str, directory: Path):
        super().__init__()
        self.prefix = prefix
        self.dir = directory
        self.stack = contextlib.ExitStack()

    def __enter__(self) -> typing.IO[bytes]:
        with self.stack as stack:
            self.file = stack.enter_context(
                tempfile.NamedTemporaryFile(
                    mode="a+b",
                    prefix=self.prefix,
                    dir=self.dir,
                    delete=False,
                ),
            )
            self.stack = stack.pop_all()
        return self.file

    def __exit__(self, exc, *_) -> None:
        self.stack.close()
        # delete on error
        if exc:
            Path(self.file.name).unlink()


class StreamReader(IO[bytes]):
    """File-like object from an httpx.Response."""

    def __init__(self, response: httpx.Response, bufsize: int = tarfile.RECORDSIZE):
        self.bufsize = bufsize
        self.stream = response.iter_raw(bufsize)
        self.hasher = hashlib.sha256()

    def read(self, size: int):
        """Read chunk from stream."""
        # To satisfy the file-like api we should be able to read an arbitrary
        # number of bytes from the stream, but the http response returns a
        # generator with a fixed chunk size. No need to go lower level to change it
        # since we know `read` will be called with the same size during extraction.
        assert size == self.bufsize
        try:
            chunk = next(self.stream)
        except StopIteration:
            return None
        self.hasher.update(chunk)
        return chunk

    def readall(self):
        """Read everything in stream while discarding chunks."""
        while self.read(self.bufsize):
            ...

    def getbuffer(self):
        """Read the entire stream into an in-memory buffer."""
        buf = io.BytesIO()
        shutil.copyfileobj(self, buf, self.bufsize)
        buf.seek(0)
        return buf

    @property
    def checksum(self) -> str:
        return self.hasher.hexdigest()


@dataclass
class Downloader:
    """Download the dagger CLI binary."""

    CLI_BASE_URL: ClassVar[str] = "https://dl.dagger.io"
    CLI_BIN_PREFIX: ClassVar[str] = "dagger-"

    version: str = CLI_VERSION
    platform: Platform = field(default_factory=get_platform, kw_only=True)
    progress: Progress = field(default_factory=Progress, kw_only=True)

    def _create_url(self, file_name: str):
        return httpx.URL(
            self.CLI_BASE_URL,
            path=f"/dagger/releases/{self.version}/{file_name}",
        )

    @property
    def archive_url(self):
        ext = "zip" if self.platform.os == "windows" else "tar.gz"
        return self._create_url(
            f"dagger_v{self.version}_{self.platform.os}_{self.platform.arch}.{ext}"
        )

    @property
    def archive_name(self):
        return PurePath(self.archive_url.path).name

    @property
    def checksum_url(self):
        return self._create_url(self.checksum_name)

    @property
    def checksum_name(self):
        return "checksums.txt"

    @functools.cached_property
    def cache_dir(self) -> Path:
        # Use the XDG_CACHE_HOME environment variable in all platforms to follow
        # https://github.com/adrg/xdg a bit more closely (used in the Go SDK).
        # See https://github.com/dagger/dagger/issues/3963
        env = os.getenv("XDG_CACHE_HOME", "").strip()
        path = Path(env).expanduser() if env else platformdirs.user_cache_path()
        cache_dir = path / "dagger"
        cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        return cache_dir

    def __await__(self):
        return self.get().__await__()

    async def get(self) -> str:
        # TODO: Convert download to async.
        return await asyncify(self.get_sync)

    def get_sync(self) -> str:
        """Download CLI to cache and return its path."""
        cli_bin_path = self.cache_dir / f"{self.CLI_BIN_PREFIX}{self.version}"

        if self.platform.os == "windows":
            cli_bin_path = cli_bin_path.with_suffix(".exe")

        if not cli_bin_path.exists():
            cli_bin_path = self._download(cli_bin_path)

        # garbage collection of old binaries
        for file in self.cache_dir.glob(f"{self.CLI_BIN_PREFIX}*"):
            if file != cli_bin_path:
                file.unlink(missing_ok=True)

        return str(cli_bin_path.absolute())

    def _download(self, path: Path) -> Path:
        logger.debug("Downloading dagger CLI from %s to %s", self.archive_url, path)
        self.progress.update_sync("Downloading dagger CLI")
        try:
            expected_hash = self.expected_checksum()
        except httpx.HTTPError as e:
            msg = f"Failed to download checksums from {self.checksum_url}: {e}"
            raise dagger.DownloadError(msg) from e

        with TempFile(f"temp-{self.CLI_BIN_PREFIX}", self.cache_dir) as tmp_bin:
            try:
                actual_hash = self.extract_cli_archive(tmp_bin)
            except httpx.HTTPError as e:
                msg = f"Failed to download archive from {self.archive_url}: {e}"
                raise dagger.DownloadError(msg) from e

            if actual_hash != expected_hash:
                msg = (
                    f"Downloaded CLI binary checksum ({actual_hash}) "
                    f"does not match expected checksum ({expected_hash})"
                )
                raise dagger.DownloadError(msg)

        tmp_bin_path = Path(tmp_bin.name)
        tmp_bin_path.chmod(0o700)
        return tmp_bin_path.rename(path)

    def expected_checksum(self) -> str:
        archive_name = self.archive_name
        with httpx.stream("GET", self.checksum_url, follow_redirects=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                checksum, filename = line.split()
                if filename == archive_name:
                    return checksum
        msg = "Could not find checksum for archive"
        raise dagger.DownloadError(msg)

    def extract_cli_archive(self, dest: IO[bytes]) -> str:
        """
        Download the CLI archive and extract the binary into the provided dest.

        Returns
        -------
        str
            The sha256 hash of the whole archive as read during download.
        """
        url = self.archive_url

        with httpx.stream("GET", url, follow_redirects=True) as r:
            r.raise_for_status()
            reader = StreamReader(r)
            extractor = (
                self._extract_from_zip
                if url.path.endswith(".zip")
                else self._extract_from_tar
            )

            with extractor(reader) as cli_bin:
                shutil.copyfileobj(cli_bin, dest)

            return reader.checksum

    @contextlib.contextmanager
    def _extract_from_tar(self, reader: StreamReader) -> Iterator[IO[bytes]]:
        with tarfile.open(mode="|gz", fileobj=reader) as tar:
            for member in tar:
                if member.name == "dagger" and (file := tar.extractfile(member)):
                    yield file
                    # ensure the entire body is read into the hash
                    reader.readall()
                    break
            else:
                msg = "There is no item named 'dagger' in the archive"
                raise dagger.DownloadError(msg)

    @contextlib.contextmanager
    def _extract_from_zip(self, reader: StreamReader) -> Iterator[IO[bytes]]:
        # TODO: extract from stream instead of loading archive into memory
        with zipfile.ZipFile(reader.getbuffer()) as zar:
            try:
                with zar.open("dagger.exe") as file:
                    yield file
            except KeyError as e:
                msg = "There is no item named 'dagger.exe' in the archive"
                raise dagger.DownloadError(msg) from e
