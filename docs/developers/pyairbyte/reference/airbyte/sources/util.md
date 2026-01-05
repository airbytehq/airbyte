---
sidebar_label: util
title: airbyte.sources.util
---

Utility functions for working with sources.

## annotations

## warnings

## Decimal

## InvalidOperation

## TYPE\_CHECKING

## Any

## get\_connector\_executor

## PyAirbyteInputError

## Source

#### get\_connector

```python
def get_connector(name: str,
                  config: dict[str, Any] | None = None,
                  *,
                  version: str | None = None,
                  pip_url: str | None = None,
                  local_executable: Path | str | None = None,
                  install_if_missing: bool = True) -> Source
```

Deprecated. Use get_source instead.

#### get\_source

```python
def get_source(name: str,
               config: dict[str, Any] | None = None,
               *,
               config_change_callback: ConfigChangeCallback | None = None,
               streams: str | list[str] | None = None,
               version: str | None = None,
               use_python: bool | Path | str | None = None,
               pip_url: str | None = None,
               local_executable: Path | str | None = None,
               docker_image: bool | str | None = None,
               use_host_network: bool = False,
               source_manifest: bool | dict | Path | str | None = None,
               install_if_missing: bool = True,
               install_root: Path | None = None,
               no_executor: bool = False) -> Source
```

Get a connector by name and version.

If an explicit install or execution method is requested (e.g. `local_executable`,
`docker_image`, `pip_url`, `source_manifest`), the connector will be executed using this method.

Otherwise, an appropriate method will be selected based on the available connector metadata:
1. If the connector is registered and has a YAML source manifest is available, the YAML manifest
will be downloaded and used to to execute the connector.
2. Else, if the connector is registered and has a PyPI package, it will be installed via pip.
3. Else, if the connector is registered and has a Docker image, and if Docker is available, it
will be executed using Docker.

**Arguments**:

- `name` - connector name
- `config` - connector config - if not provided, you need to set it later via the set_config
  method.
- `config_change_callback` - callback function to be called when the connector config changes.
- `streams` - list of stream names to select for reading. If set to &quot;*&quot;, all streams will be
  selected. If not provided, you can set it later via the `select_streams()` or
  `select_all_streams()` method.
- `docker_image`0 - connector version - if not provided, the currently installed version will be used.
  If no version is installed, the latest available version will be used. The version can
  also be set to &quot;latest&quot; to force the use of the latest available version.
- `docker_image`1 - (Optional.) Python interpreter specification:
  - True: Use current Python interpreter. (Inferred if `pip_url` is set.)
  - False: Use Docker instead.
  - Path: Use interpreter at this path.
  - str: Use specific Python version. E.g. &quot;3.11&quot; or &quot;3.11.10&quot;. If the version is not yet
  installed, it will be installed by uv. (This generally adds less than 3 seconds
  to install times.)
- `pip_url` - connector pip URL - if not provided, the pip url will be inferred from the
  connector name.
- `local_executable` - If set, the connector will be assumed to already be installed and will be
  executed using this path or executable name. Otherwise, the connector will be installed
  automatically in a virtual environment.
- `docker_image` - If set, the connector will be executed using Docker. You can specify `docker_image`6
  to use the default image for the connector, or you can specify a custom image name.
  If `docker_image`0 is specified and your image name does not already contain a tag
  (e.g. `docker_image`8), the version will be appended as a tag (e.g. `docker_image`9).
- `pip_url`0 - If set, along with docker_image, the connector will be executed using
  the host network. This is useful for connectors that need to access resources on
  the host machine, such as a local database. This parameter is ignored when
  `docker_image` is not set.
- `source_manifest` - If set, the connector will be executed based on a declarative YAML
  source definition. This input can be `docker_image`6 to attempt to auto-download a YAML spec,
  `pip_url`4 to accept a Python dictionary as the manifest, `pip_url`5 to pull a manifest from
  the local file system, or `pip_url`6 to pull the definition from a web URL.
- `pip_url`7 - Whether to install the connector if it is not available locally. This
  parameter is ignored when `local_executable` or `source_manifest` are set.
- `source_manifest`0 - (Optional.) The root directory where the virtual environment will be
  created. If not provided, the current working directory will be used.
- `source_manifest`1 - If True, use NoOpExecutor which fetches specs from the registry without
  local installation. This is useful for scenarios where you need to validate
  configurations but don&#x27;t need to run the connector locally (e.g., deploying to Cloud).

#### get\_benchmark\_source

```python
def get_benchmark_source(num_records: int | str = "5e5",
                         *,
                         install_if_missing: bool = True) -> Source
```

Get a source for benchmarking.

This source will generate dummy records for performance benchmarking purposes.
You can specify the number of records to generate using the `num_records` parameter.
The `num_records` parameter can be an integer or a string in scientific notation.
For example, `"5e6"` will generate 5 million records. If underscores are providing
within a numeric a string, they will be ignored.

**Arguments**:

- `num_records` - The number of records to generate. Defaults to &quot;5e5&quot;, or
  500,000 records.
  Can be an integer (`1000`) or a string in scientific notation.
  For example, `"5e6"` will generate 5 million records.
- `install_if_missing` - Whether to install the source if it is not available locally.
  

**Returns**:

- `Source` - The source object for benchmarking.

#### \_\_all\_\_

