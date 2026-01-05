---
sidebar_label: local
title: airbyte._executors.local
---

## annotations

## TYPE\_CHECKING

## NoReturn

## exc

## Executor

## PathExecutor Objects

```python
class PathExecutor(Executor)
```

#### \_\_init\_\_

```python
def __init__(name: str | None = None,
             *,
             path: Path,
             target_version: str | None = None) -> None
```

Initialize a connector executor that runs a connector from a local path.

If path is simply the name of the connector, it will be expected to exist in the current
PATH or in the current working directory.

#### ensure\_installation

```python
def ensure_installation(*, auto_fix: bool = True) -> None
```

Ensure that the connector executable can be found.

The auto_fix parameter is ignored for this executor type.

#### install

```python
def install() -> NoReturn
```

#### uninstall

```python
def uninstall() -> NoReturn
```

#### \_cli

```python
@property
def _cli() -> list[str]
```

Get the base args of the CLI executable.

