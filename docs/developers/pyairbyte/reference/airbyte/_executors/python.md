---
sidebar_label: python
title: airbyte._executors.python
---

## annotations

## shlex

## subprocess

## sys

## suppress

## Path

## rmtree

## TYPE\_CHECKING

## Literal

## overrides

## print

## exc

## Executor

## is\_windows

## EventState

## log\_install\_state

## get\_bin\_dir

## DEFAULT\_INSTALL\_DIR

## NO\_UV

## VenvExecutor Objects

```python
class VenvExecutor(Executor)
```

#### \_\_init\_\_

```python
def __init__(name: str | None = None,
             *,
             metadata: ConnectorMetadata | None = None,
             target_version: str | None = None,
             pip_url: str | None = None,
             install_root: Path | None = None,
             use_python: bool | Path | str | None = None) -> None
```

Initialize a connector executor that runs a connector in a virtual environment.

**Arguments**:

- `name` - The name of the connector.
- `metadata` - (Optional.) The metadata of the connector.
- `target_version` - (Optional.) The version of the connector to install.
- `pip_url` - (Optional.) The pip URL of the connector to install.
- `install_root` - (Optional.) The root directory where the virtual environment will be
  created. If not provided, the current working directory will be used.
- `use_python` - (Optional.) Python interpreter specification:
  - True: Use current Python interpreter
  - False: Use Docker instead (handled by factory)
  - Path: Use interpreter at this path or interpreter name/command
  - str: Use uv-managed Python version (semver patterns like &quot;3.12&quot;, &quot;3.11.5&quot;)

#### \_get\_venv\_name

```python
def _get_venv_name() -> str
```

#### \_get\_venv\_path

```python
def _get_venv_path() -> Path
```

#### \_get\_connector\_path

```python
def _get_connector_path() -> Path
```

#### interpreter\_path

```python
@property
def interpreter_path() -> Path
```

#### \_run\_subprocess\_and\_raise\_on\_failure

```python
def _run_subprocess_and_raise_on_failure(args: list[str]) -> None
```

#### uninstall

```python
def uninstall() -> None
```

#### docs\_url

```python
@property
def docs_url() -> str
```

Get the URL to the connector&#x27;s documentation.

#### install

```python
def install() -> None
```

Install the connector in a virtual environment.

After installation, the installed version will be stored in self.reported_version.

#### get\_installed\_version

```python
@overrides
def get_installed_version(*,
                          raise_on_error: bool = False,
                          recheck: bool = False) -> str | None
```

Detect the version of the connector installed.

Returns the version string if it can be detected, otherwise None.

If raise_on_error is True, raise an exception if the version cannot be detected.

If recheck if False and the version has already been detected, return the cached value.

In the venv, we run the following:
&gt; python -c &quot;from importlib.metadata import version; print(version(&#x27;&lt;connector-name&gt;&#x27;))&quot;

#### ensure\_installation

```python
def ensure_installation(*, auto_fix: bool = True) -> None
```

Ensure that the connector is installed in a virtual environment.

If not yet installed and if install_if_missing is True, then install.

Optionally, verify that the installed version matches the target version.

Note: Version verification is not supported for connectors installed from a
local path.

#### \_cli

```python
@property
def _cli() -> list[str]
```

Get the base args of the CLI executable.

