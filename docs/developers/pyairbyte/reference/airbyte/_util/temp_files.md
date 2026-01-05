---
sidebar_label: temp_files
title: airbyte._util.temp_files
---

Internal helper functions for working with temporary files.

## annotations

## json

## stat

## tempfile

## time

## warnings

## contextmanager

## suppress

## Path

## TYPE\_CHECKING

## Any

## TEMP\_DIR\_OVERRIDE

#### as\_temp\_files

```python
@contextmanager
def as_temp_files(
        files_contents: list[dict | str]) -> Generator[list[str], Any, None]
```

Write the given contents to temporary files and yield the file paths as strings.

