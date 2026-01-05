---
sidebar_label: docker
title: airbyte._executors.docker
---

## annotations

## logging

## shutil

## subprocess

## suppress

## Path

## exc

## Executor

#### logger

#### DEFAULT\_AIRBYTE\_CONTAINER\_TEMP\_DIR

Default temp dir in an Airbyte connector&#x27;s Docker image.

## DockerExecutor Objects

```python
class DockerExecutor(Executor)
```

#### \_\_init\_\_

```python
def __init__(name: str,
             image_name_full: str,
             *,
             executable: list[str],
             target_version: str | None = None,
             volumes: dict[Path, str] | None = None) -> None
```

#### ensure\_installation

```python
def ensure_installation(*, auto_fix: bool = True) -> None
```

Ensure that the connector executable can be found.

The auto_fix parameter is ignored for this executor type.

#### install

```python
def install() -> None
```

Install the connector.

For docker images, for now this is a no-op. In the future we might
pull the Docker image in this step.

#### uninstall

```python
def uninstall() -> None
```

Uninstall the connector.

For docker images, this operation runs an `docker rmi` command to remove the image.

We suppress any errors that occur during the removal process.

#### \_cli

```python
@property
def _cli() -> list[str]
```

Get the base args of the CLI executable.

#### map\_cli\_args

```python
def map_cli_args(args: list[str]) -> list[str]
```

Map local file paths to the container&#x27;s volume paths.

