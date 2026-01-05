---
sidebar_label: declarative
title: airbyte._executors.declarative
---

Support for declarative yaml source testing.

## annotations

## hashlib

## warnings

## Path

## IO

## TYPE\_CHECKING

## Any

## cast

## pydantic

## yaml

## AirbyteEntrypoint

## ConcurrentDeclarativeSource

## Executor

#### \_suppress\_cdk\_pydantic\_deprecation\_warnings

```python
def _suppress_cdk_pydantic_deprecation_warnings() -> None
```

Suppress deprecation warnings from Pydantic in the CDK.

CDK has deprecated uses of `json()` and `parse_obj()`, and we don&#x27;t want users
to see these warnings.

## DeclarativeExecutor Objects

```python
class DeclarativeExecutor(Executor)
```

An executor for declarative sources.

#### \_\_init\_\_

```python
def __init__(name: str,
             manifest: dict | Path,
             components_py: str | Path | None = None,
             components_py_checksum: str | None = None) -> None
```

Initialize a declarative executor.

- If `manifest` is a path, it will be read as a json file.
- If `manifest` is a string, it will be parsed as an HTTP path.
- If `manifest` is a dict, it will be used as is.
- If `components_py` is provided, components will be injected into the source.
- If `components_py_checksum` is not provided, it will be calculated automatically.

#### declarative\_source

```python
@property
def declarative_source() -> ConcurrentDeclarativeSource
```

Get the declarative source object.

**Notes**:

  1. Since Sep 2025, the declarative source class used is `ConcurrentDeclarativeSource`.
  2. The `ConcurrentDeclarativeSource` object sometimes doesn&#x27;t want to be read from twice,
  likely due to threads being already shut down after a successful read.
  3. Rather than cache the source object, we recreate it each time we need it, to
  avoid any issues with re-using the same object.

#### get\_installed\_version

```python
def get_installed_version(*,
                          raise_on_error: bool = False,
                          recheck: bool = False) -> str | None
```

Detect the version of the connector installed.

#### \_cli

```python
@property
def _cli() -> list[str]
```

Not applicable.

#### execute

```python
def execute(args: list[str],
            *,
            stdin: IO[str] | AirbyteMessageIterator | None = None,
            suppress_stderr: bool = False) -> Iterator[str]
```

Execute the declarative source.

#### ensure\_installation

```python
def ensure_installation(*, auto_fix: bool = True) -> None
```

No-op. The declarative source is included with PyAirbyte.

#### install

```python
def install() -> None
```

No-op. The declarative source is included with PyAirbyte.

#### uninstall

```python
def uninstall() -> None
```

No-op. The declarative source is included with PyAirbyte.

