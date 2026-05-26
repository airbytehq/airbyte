#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Disk-backed external merge sort used by the Shopify bulk GraphQL streams.

Large bulk GraphQL result sets (for example, the metafield streams) used to be
globally sorted in memory with Python's builtin `sorted()` before emission,
which materialized every record at once and caused out-of-memory failures on
large slices. `external_stable_sort` replaces that in-memory sort with a
stable, streaming, disk-backed sort: records are accumulated into fixed-size
chunks, each chunk is sorted in memory, chunks that exceed the in-memory
budget are spilled as sorted runs to temp files, and the final output is a
k-way heap merge across those runs.

The sort is **stable**: when two records have equal sort keys, the record that
arrived first in the input iterable is emitted first in the output. That
matches the prior `sorted()` behavior and preserves the existing checkpoint
and state semantics for the Shopify bulk streams.

When the entire input fits in a single chunk, the implementation skips the
spill-and-merge path entirely and sorts in place, so small slices pay no disk
cost.
"""

import heapq
import json
import logging
import os
import tempfile
from typing import Any, Callable, Iterable, Iterator, List, Mapping, Optional


logger = logging.getLogger("airbyte")


DEFAULT_SORT_CHUNK_SIZE = 50_000


def external_stable_sort(
    records: Iterable[Mapping[str, Any]],
    key_fn: Callable[[Mapping[str, Any]], Any],
    chunk_size: int = DEFAULT_SORT_CHUNK_SIZE,
    tmp_dir: Optional[str] = None,
) -> Iterator[Mapping[str, Any]]:
    """Stably sort `records` by `key_fn` using bounded memory.

    Records are consumed lazily from the input iterable in chunks of at most
    `chunk_size`. Each chunk is sorted in memory by `(key_fn(record), ordinal)`
    where `ordinal` is a monotonically increasing insertion counter that
    guarantees stability. Chunks beyond the first are spilled to temporary
    JSON-lines files and then streamed back through a k-way heap merge.

    The output iterator is generator-based and yields records one at a time,
    so callers can pipe results into downstream filters without materializing
    the full sorted output in memory.

    Temp files are always cleaned up — on normal completion, on generator
    close, and on exceptions raised from downstream consumers.
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be a positive integer, got {chunk_size}")

    chunk: List[Any] = []
    run_paths: List[str] = []
    ordinal = 0

    try:
        for record in records:
            chunk.append((key_fn(record), ordinal, record))
            ordinal += 1
            if len(chunk) >= chunk_size:
                _spill_chunk(chunk, tmp_dir, run_paths)
                chunk = []

        if not run_paths:
            # Fast path: entire input fits in one in-memory chunk, so we skip
            # the spill-and-merge pipeline entirely.
            chunk.sort(key=_sort_key)
            for _, _, record in chunk:
                yield record
            return

        if chunk:
            _spill_chunk(chunk, tmp_dir, run_paths)

        logger.info(f"External sort spilled {len(run_paths)} run file(s) covering {ordinal} record(s); merging.")
        yield from _merge_runs(run_paths)
    finally:
        _cleanup_runs(run_paths)


def _sort_key(item: Any) -> Any:
    # item is (key, ordinal, record). Tuples compare lexicographically, so the
    # ordinal acts as a stable secondary key for equal primary keys.
    return (item[0], item[1])


def _spill_chunk(chunk: List[Any], tmp_dir: Optional[str], run_paths: List[str]) -> None:
    """Sort `chunk` in place and write it as a new sorted run file.

    The newly created path is appended to `run_paths` **before** any write
    begins, so a failure in `json.dumps` or `fh.write` still leaves the path
    visible to the outer `finally` block for cleanup. Each line is a
    JSON-encoded `[key, ordinal, record]` triple, deserialized during merge.
    """
    chunk.sort(key=_sort_key)
    fd, path = tempfile.mkstemp(prefix="shopify_bulk_sort_", suffix=".jsonl", dir=tmp_dir)
    run_paths.append(path)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        for key, ord_value, record in chunk:
            fh.write(json.dumps([key, ord_value, record], separators=(",", ":")) + "\n")


def _iter_run(path: str) -> Iterator[Any]:
    """Yield `(key, ordinal, record)` triples from a spilled run file."""
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            key, ord_value, record = json.loads(line)
            yield (key, ord_value, record)


def _merge_runs(run_paths: List[str]) -> Iterator[Mapping[str, Any]]:
    """Stream the merged output of all run files in sorted order."""
    run_iters = [_iter_run(path) for path in run_paths]
    for _, _, record in heapq.merge(*run_iters, key=_sort_key):
        yield record


def _cleanup_runs(run_paths: List[str]) -> None:
    """Best-effort removal of spilled run files. Missing files are ignored."""
    for path in run_paths:
        try:
            os.unlink(path)
        except FileNotFoundError:
            # Already removed (for example, by tempfile cleanup on container
            # shutdown). Best-effort cleanup is intentionally silent here.
            pass
        except OSError as exc:
            logger.warning(f"Failed to remove external-sort spill file `{path}`: {exc}")
