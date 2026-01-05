---
sidebar_label: _connector_base
title: airbyte._connector_base
---

Destination base classes.

## annotations

## abc

## json

## sys

## Path

## sleep

## TYPE\_CHECKING

## Any

## Literal

## jsonschema

## rich

## yaml

## Syntax

## AirbyteMessage

## ConnectorSpecification

## OrchestratorType

## Status

## TraceType

## Type

## exc

## ConnectorRuntimeInfo

## one\_way\_hash

## EventState

## log\_config\_validation\_result

## log\_connector\_check\_result

## as\_temp\_files

## new\_passthrough\_file\_logger

## hydrate\_secrets

#### MAX\_LOG\_LINES

## ConnectorBase Objects

```python
class ConnectorBase(abc.ABC)
```

A class representing a destination that can be called.

#### connector\_type

#### \_\_init\_\_

```python
def __init__(executor: Executor,
             name: str,
             config: dict[str, Any] | None = None,
             config_change_callback: ConfigChangeCallback | None = None,
             *,
             validate: bool = False) -> None
```

Initialize the source.

If config is provided, it will be validated against the spec if validate is True.

#### name

```python
@property
def name() -> str
```

Get the name of the connector.

#### \_get\_connector\_runtime\_info

```python
def _get_connector_runtime_info() -> ConnectorRuntimeInfo
```

Get metadata for telemetry and performance logging.

#### \_print\_info\_message

```python
def _print_info_message(message: str) -> None
```

Print a message to the logger.

#### \_print\_error\_message

```python
def _print_error_message(message: str) -> None
```

Print a message to the console and the logger.

#### set\_config

```python
def set_config(config: dict[str, Any], *, validate: bool = True) -> None
```

Set the config for the connector.

If validate is True, raise an exception if the config fails validation.

If validate is False, validation will be deferred until check() or validate_config()
is called.

#### get\_config

```python
def get_config() -> dict[str, Any]
```

Get the config for the connector.

If secrets are passed by reference (`secret_reference::*`), this will return the raw config
dictionary without secrets hydrated.

#### \_hydrated\_config

```python
@property
def _hydrated_config() -> dict[str, Any]
```

Internal property used to get a hydrated config dictionary.

This will have secrets hydrated, so it can be passed to the connector.

#### config\_hash

```python
@property
def config_hash() -> str | None
```

Get a hash of the current config.

Returns None if the config is not set.

#### validate\_config

```python
def validate_config(config: dict[str, Any] | None = None) -> None
```

Validate the config against the spec.

If config is not provided, the already-set config will be validated.

#### \_get\_spec

```python
def _get_spec(*, force_refresh: bool = False) -> ConnectorSpecification
```

Call spec on the connector.

This involves the following steps:
* execute the connector with spec
* Listen to the messages and return the first AirbyteCatalog that comes along.
* Make sure the subprocess is killed when the function returns.

**Raises**:

- `AirbyteConnectorSpecFailedError` - If the spec operation fails.
- `AirbyteConnectorMissingSpecError` - If the spec operation does not return a spec.

#### config\_spec

```python
@property
def config_spec() -> dict[str, Any]
```

Generate a configuration spec for this connector, as a JSON Schema definition.

This function generates a JSON Schema dictionary with configuration specs for the
current connector, as a dictionary.

**Returns**:

- `dict` - The JSON Schema configuration spec as a dictionary.

#### print\_config\_spec

```python
def print_config_spec(format: Literal["yaml", "json"] = "yaml",
                      *,
                      output_file: Path | str | None = None,
                      stderr: bool = False) -> None
```

Print the configuration spec for this connector.

**Arguments**:

- `format` - The format to print the spec in. Must be &quot;yaml&quot; or &quot;json&quot;.
- `output_file` - Optional. If set, the spec will be written to the given file path.
  Otherwise, it will be printed to the console.
- `stderr` - If True, print to stderr instead of stdout. This is useful when we
  want to print the spec to the console but not interfere with other output.

#### \_yaml\_spec

```python
@property
def _yaml_spec() -> str
```

Get the spec as a yaml string.

For now, the primary use case is for writing and debugging a valid config for a source.

This is private for now because we probably want better polish before exposing this
as a stable interface. This will also get easier when we have docs links with this info
for each connector.

#### docs\_url

```python
@property
def docs_url() -> str
```

Get the URL to the connector&#x27;s documentation.

#### connector\_version

```python
@property
def connector_version() -> str | None
```

Return the version of the connector as reported by the executor.

Returns None if the version cannot be determined.

#### check

```python
def check() -> None
```

Call check on the connector.

This involves the following steps:
* Write the config to a temporary file
* execute the connector with check --config &lt;config_file&gt;
* Listen to the messages and return the first AirbyteCatalog that comes along.
* Make sure the subprocess is killed when the function returns.

#### install

```python
def install() -> None
```

Install the connector if it is not yet installed.

#### uninstall

```python
def uninstall() -> None
```

Uninstall the connector if it is installed.

This only works if the use_local_install flag wasn&#x27;t used and installation is managed by
PyAirbyte.

#### \_peek\_airbyte\_message

```python
def _peek_airbyte_message(message: AirbyteMessage,
                          *,
                          raise_on_error: bool = True) -> None
```

Process an Airbyte message.

This method handles reading Airbyte messages and taking action, if needed, based on the
message type. For instance, log messages are logged, records are tallied, and errors are
raised as exceptions if `raise_on_error` is True. If a config change message is received,
the config change callback is called.

**Raises**:

- `AirbyteConnectorFailedError` - If a TRACE message of type ERROR is emitted.

#### \_execute

```python
def _execute(
    args: list[str],
    stdin: IO[str] | AirbyteMessageIterator | None = None,
    *,
    progress_tracker: ProgressTracker | None = None
) -> Generator[AirbyteMessage, None, None]
```

Execute the connector with the given arguments.

This involves the following steps:
* Locate the right venv. It is called &quot;.venv-&lt;connector_name&gt;&quot;
* Spawn a subprocess with .venv-&lt;connector_name&gt;/bin/&lt;connector-name&gt; &lt;args&gt;
* Read the output line by line of the subprocess and serialize them AirbyteMessage objects.
Drop if not valid.

**Raises**:

- `AirbyteConnectorFailedError` - If the process returns a failure status (non-zero).

#### \_\_all\_\_

