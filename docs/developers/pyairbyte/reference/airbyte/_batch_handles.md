---
sidebar_label: _batch_handles
title: airbyte._batch_handles
---

Batch handle class.

## annotations

## suppress

## IO

## TYPE\_CHECKING

## BatchHandle Objects

```python
class BatchHandle()
```

A handle for a batch of records.

#### \_\_init\_\_

```python
def __init__(stream_name: str, batch_id: str, files: list[Path],
             file_opener: Callable[[Path], IO[str]]) -> None
```

Initialize the batch handle.

#### files

```python
@property
def files() -> list[Path]
```

Return the files.

#### batch\_id

```python
@property
def batch_id() -> str
```

Return the batch ID.

#### stream\_name

```python
@property
def stream_name() -> str
```

Return the stream name.

#### record\_count

```python
@property
def record_count() -> int
```

Return the record count.

#### increment\_record\_count

```python
def increment_record_count() -> None
```

Increment the record count.

#### open\_file\_writer

```python
@property
def open_file_writer() -> IO[str] | None
```

Return the open file writer, if any, or None.

#### close\_files

```python
def close_files() -> None
```

Close the file writer.

#### delete\_files

```python
def delete_files() -> None
```

Delete the files.

If any files are open, they will be closed first.
If any files are missing, they will be ignored.

#### \_\_del\_\_

```python
def __del__() -> None
```

Upon deletion, close the file writer.

