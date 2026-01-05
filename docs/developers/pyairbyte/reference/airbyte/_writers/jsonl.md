---
sidebar_label: jsonl
title: airbyte._writers.jsonl
---

A Parquet cache implementation.

## annotations

## gzip

## json

## IO

## TYPE\_CHECKING

## cast

## orjson

## overrides

## FileWriterBase

## JsonlWriter Objects

```python
class JsonlWriter(FileWriterBase)
```

A Jsonl cache implementation.

#### default\_cache\_file\_suffix

#### prune\_extra\_fields

#### \_open\_new\_file

```python
@overrides
def _open_new_file(file_path: Path) -> IO[str]
```

Open a new file for writing.

#### \_write\_record\_dict

```python
@overrides
def _write_record_dict(record_dict: StreamRecord,
                       open_file_writer: IO[str]) -> None
```

