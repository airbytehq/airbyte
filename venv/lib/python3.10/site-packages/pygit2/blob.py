import io
import threading
import time
from contextlib import AbstractContextManager
from typing import Optional
from queue import Queue

from ._pygit2 import GIT_BLOB_FILTER_CHECK_FOR_BINARY, Blob, Oid


class _BlobIO(io.RawIOBase):
    """Low-level wrapper for streaming blob content.

    The underlying libgit2 git_writestream filter chain will be run
    in a separate thread. The GIL will be released while running
    libgit2 filtering.
    """

    def __init__(
        self,
        blob: Blob,
        as_path: Optional[str] = None,
        flags: int = GIT_BLOB_FILTER_CHECK_FOR_BINARY,
        commit_id: Optional[Oid] = None,
    ):
        super().__init__()
        self._blob = blob
        self._queue = Queue(maxsize=1)
        self._ready = threading.Event()
        self._writer_closed = threading.Event()
        self._chunk: Optional[bytes] = None
        self._thread = threading.Thread(
            target=self._blob._write_to_queue,
            args=(self._queue, self._ready, self._writer_closed),
            kwargs={
                "as_path": as_path,
                "flags": flags,
                "commit_id": commit_id,
            },
            daemon=True,
        )
        self._thread.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def isatty():
        return False

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return False

    def readinto(self, b, /):
        try:
            while self._chunk is None:
                self._ready.wait()
                if self._queue.empty():
                    if self._writer_closed.is_set():
                        # EOF
                        return 0
                    self._ready.clear()
                    time.sleep(0)
                    continue
                chunk = self._queue.get()
                if chunk:
                    self._chunk = chunk

            if len(self._chunk) <= len(b):
                bytes_written = len(self._chunk)
                b[:bytes_written] = self._chunk
                self._chunk = None
                return bytes_written
            bytes_written = len(b)
            b[:] = self._chunk[:bytes_written]
            self._chunk = self._chunk[bytes_written:]
            return bytes_written
        except KeyboardInterrupt:
            return 0

    def close(self):
        try:
            self._ready.wait()
            self._writer_closed.wait()
            while self._queue is not None and not self._queue.empty():
                self._queue.get()
            self._thread.join()
        except KeyboardInterrupt:
            pass
        self._queue = None


class BlobIO(io.BufferedReader, AbstractContextManager):
    """Read-only wrapper for streaming blob content.

    Supports reading both raw and filtered blob content.
    Implements io.BufferedReader.

    Example:

        >>> with BlobIO(blob) as f:
        ...     while True:
        ...         # Read blob data in 1KB chunks until EOF is reached
        ...         chunk = f.read(1024)
        ...         if not chunk:
        ...             break

    By default, `BlobIO` will stream the raw contents of the blob, but it
    can also be used to stream filtered content (i.e. to read the content
    after applying filters which would be used when checking out the blob
    to the working directory).

    Example:

        >>> with BlobIO(blob, as_path='my_file.ext') as f:
        ...     # Read the filtered content which would be returned upon
        ...     # running 'git checkout -- my_file.txt'
        ...     filtered_data = f.read()
    """

    def __init__(
        self,
        blob: Blob,
        as_path: Optional[str] = None,
        flags: int = GIT_BLOB_FILTER_CHECK_FOR_BINARY,
        commit_id: Optional[Oid] = None,
    ):
        """Wrap the specified blob.

        Parameters:
            blob: The blob to wrap.
            as_path: Filter the contents of the blob as if it had the specified
                path. If `as_path` is None, the raw contents of the blob will
                be read.
            flags: GIT_BLOB_FILTER_* bitflags (only applicable when `as_path`
                is set).
            commit_oid: Commit to load attributes from when
                GIT_BLOB_FILTER_ATTRIBUTES_FROM_COMMIT is specified in `flags`
                (only applicable when `as_path` is set).
        """
        raw = _BlobIO(blob, as_path=as_path, flags=flags, commit_id=commit_id)
        super().__init__(raw)

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


io.RawIOBase.register(_BlobIO)
io.BufferedIOBase.register(BlobIO)
