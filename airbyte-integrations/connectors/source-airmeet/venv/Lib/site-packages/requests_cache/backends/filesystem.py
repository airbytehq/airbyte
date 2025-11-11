"""Filesystem cache backend. For usage details, see :ref:`Backends: Filesystem <filesystem>`.

.. automodsumm:: requests_cache.backends.filesystem
   :classes-only:
   :nosignatures:
"""

from contextlib import contextmanager
from os import makedirs
from pathlib import Path
from pickle import PickleError
from shutil import rmtree
from threading import RLock
from typing import Iterator, Optional

from ..serializers import SERIALIZERS, SerializerType, json_serializer
from . import BaseCache, BaseStorage, StrOrPath
from .sqlite import SQLiteDict, get_cache_path


class FileCache(BaseCache):
    """Filesystem cache backend.

    Args:
        cache_name: Base directory for cache files
        use_cache_dir: Store database in a user cache directory (e.g., `~/.cache/`)
        use_temp: Store cache files in a temp directory (e.g., ``/tmp/http_cache/``).
            Note: if ``cache_name`` is an absolute path, this option will be ignored.
        decode_content: Decode JSON or text response body into a human-readable format
        extension: Extension for cache files. If not specified, the serializer default extension
            will be used.
    """

    def __init__(
        self,
        cache_name: StrOrPath = 'http_cache',
        use_temp: bool = False,
        decode_content: bool = True,
        serializer: Optional[SerializerType] = None,
        **kwargs,
    ):
        super().__init__(cache_name=str(cache_name), **kwargs)
        skwargs = {'serializer': serializer, **kwargs} if serializer else kwargs
        self.responses: FileDict = FileDict(
            cache_name, use_temp=use_temp, decode_content=decode_content, **skwargs
        )
        self.redirects: SQLiteDict = SQLiteDict(
            self.cache_dir / 'redirects.sqlite', 'redirects', serializer=None, **kwargs
        )

    @property
    def cache_dir(self) -> Path:
        """Base directory for cache files"""
        return Path(self.responses.cache_dir)

    def paths(self) -> Iterator[Path]:
        """Get absolute file paths to all cached responses"""
        return self.responses.paths()

    def clear(self):
        """Clear the cache"""
        # FileDict.clear() removes the cache directory, including redirects.sqlite
        self.responses.clear()
        self.redirects.init_db()

    def delete(self, *args, **kwargs):
        with self.responses._lock:
            return super().delete(*args, **kwargs)


class FileDict(BaseStorage):
    """A dictionary-like interface to files on the local filesystem"""

    def __init__(
        self,
        cache_name: StrOrPath,
        use_temp: bool = False,
        use_cache_dir: bool = False,
        extension: Optional[str] = None,
        serializer: Optional[SerializerType] = json_serializer,
        **kwargs,
    ):
        super().__init__(serializer=serializer, **kwargs)
        self.cache_dir = get_cache_path(cache_name, use_cache_dir=use_cache_dir, use_temp=use_temp)
        self.extension = _get_extension(extension, self.serializer)
        self.is_binary = getattr(self.serializer, 'is_binary', False)
        self._lock = RLock()
        makedirs(self.cache_dir, exist_ok=True)

    @contextmanager
    def _try_io(self, ignore_errors: bool = False):
        """Attempt an I/O operation, and either ignore errors or re-raise them as KeyErrors"""
        try:
            with self._lock:
                yield
        except (EOFError, IOError, OSError, PickleError) as e:
            if not ignore_errors:
                raise KeyError from e

    def _path(self, key) -> Path:
        return self.cache_dir / f'{key}{self.extension}'

    def __getitem__(self, key):
        mode = 'rb' if self.is_binary else 'r'
        with self._try_io():
            with self._path(key).open(mode) as f:
                return self.deserialize(key, f.read())

    def __delitem__(self, key):
        with self._try_io():
            self._path(key).unlink()

    def __setitem__(self, key, value):
        with self._try_io():
            with self._path(key).open(mode='wb' if self.is_binary else 'w') as f:
                f.write(self.serialize(value))

    def __iter__(self):
        yield from self.keys()

    def __len__(self):
        return sum(1 for _ in self.paths())

    def clear(self):
        with self._try_io(ignore_errors=True):
            rmtree(self.cache_dir, ignore_errors=True)
            self.cache_dir.mkdir()

    def keys(self):
        return [path.stem for path in self.paths()]

    def paths(self) -> Iterator[Path]:
        """Get absolute file paths to all cached responses"""
        with self._lock:
            return self.cache_dir.glob(f'*{self.extension}')


def _get_extension(extension: Optional[str] = None, serializer=None) -> str:
    """Use either the provided file extension, or get the serializer's default extension"""
    if extension:
        return f'.{extension}'
    for name, obj in SERIALIZERS.items():
        if serializer is obj:
            return '.' + name.replace('pickle', 'pkl')
    return ''
