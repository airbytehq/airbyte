---
sidebar_label: util
title: airbyte._executors.util
---

## annotations

## hashlib

## sys

## tempfile

## Path

## TYPE\_CHECKING

## Literal

## cast

## requests

## yaml

## print

## exc

## DeclarativeExecutor

## DEFAULT\_AIRBYTE\_CONTAINER\_TEMP\_DIR

## DockerExecutor

## PathExecutor

## NoOpExecutor

## VenvExecutor

## which

## EventState

## log\_install\_state

## AIRBYTE\_OFFLINE\_MODE

## DEFAULT\_PROJECT\_DIR

## TEMP\_DIR\_OVERRIDE

## ConnectorMetadata

## InstallType

## get\_connector\_metadata

## get\_version

#### VERSION\_LATEST

#### DEFAULT\_MANIFEST\_URL

#### DEFAULT\_COMPONENTS\_URL

#### \_try\_get\_manifest\_connector\_files

```python
def _try_get_manifest_connector_files(
        source_name: str,
        version: str | None = None) -> tuple[dict, str | None, str | None]
```

Try to get source manifest and components.py from URLs.

Returns tuple of (manifest_dict, components_py_content, components_py_checksum).
Components values are None if components.py is not found (404 is handled gracefully).

**Raises**:

  - `PyAirbyteInputError`: If `source_name` is `None`.
  - `AirbyteConnectorInstallationError`: If the manifest cannot be downloaded or parsed,
  or if components.py cannot be downloaded (excluding 404 errors).

#### \_get\_local\_executor

```python
def _get_local_executor(name: str,
                        local_executable: Path | str | Literal[True],
                        version: str | None) -> Executor
```

Get a local executor for a connector.

#### get\_connector\_executor

```python
def get_connector_executor(name: str,
                           *,
                           version: str | None = None,
                           pip_url: str | None = None,
                           local_executable: Path | str | None = None,
                           docker_image: bool | str | None = None,
                           use_host_network: bool = False,
                           source_manifest: bool | dict | Path | str
                           | None = None,
                           install_if_missing: bool = True,
                           install_root: Path | None = None,
                           use_python: bool | Path | str | None = None,
                           no_executor: bool = False) -> Executor
```

This factory function creates an executor for a connector.

For documentation of each arg, see the function `airbyte.sources.util.get_source()`.

