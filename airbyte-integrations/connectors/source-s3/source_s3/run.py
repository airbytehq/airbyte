#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations


def _cap_malloc_arenas() -> None:
    """
    Cap glibc malloc arenas to keep peak RSS low under the concurrent file-based
    read path. With the default `8 x N_CPUs` arenas, the source pod can pin 1+ GB
    of allocator overhead that is never returned to the OS, which combined with
    the in-flight working set pushes the pod over its 2 Gi memory limit on
    streams with many or large files (oncall #12663).

    glibc-only. No-op on macOS or musl-libc images; falls back to default
    behavior, which is correct for those platforms.
    """
    try:
        import ctypes

        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        # M_ARENA_MAX = -8 from glibc's malloc.h. Equivalent to setting the
        # MALLOC_ARENA_MAX environment variable, but applied at process start
        # so it is scoped to this connector only.
        libc.mallopt(-8, 2)
    except (OSError, AttributeError):
        pass


_cap_malloc_arenas()

from source_s3.v4 import SourceS3


def run() -> None:
    SourceS3.launch()