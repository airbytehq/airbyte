---
id: airbyte-logs
title: airbyte.logs
---

PyAirbyte Logging features and related configuration.

By default, PyAirbyte main logs are written to a file in the `AIRBYTE_LOGGING_ROOT` directory, which
defaults to a system-created temporary directory. PyAirbyte also maintains connector-specific log
files within the same directory, under a subfolder with the name of the connector.

PyAirbyte supports structured JSON logging, which is disabled by default. To enable structured
logging in JSON, set `AIRBYTE_STRUCTURED_LOGGING` to `True`.

- **`AIRBYTE_LOGGING_ROOT`**&nbsp;(`pathlib.Path | None`)

  The root directory for Airbyte logs.

  This value can be overridden by setting the `AIRBYTE_LOGGING_ROOT` environment variable.

  If not provided, PyAirbyte will use `/tmp/airbyte/logs/` where `/tmp/` is the OS's default
  temporary directory. If the directory cannot be created, PyAirbyte will log a warning and
  set this value to `None`.

- **`AIRBYTE_STRUCTURED_LOGGING`**&nbsp;(`bool`)

  Whether to enable structured logging.

  This value is read from the `AIRBYTE_STRUCTURED_LOGGING` environment variable. If the variable is
  not set, the default value is `False`.

### `get_global_file_logger` {#airbyte.logs.get_global_file_logger}

<ApiMember kind="function">

<ApiSignature>

```python
def get_global_file_logger() -> logging.Logger | None
```

</ApiSignature>

Return the global logger for PyAirbyte.

This logger is configured to write logs to the console and to a file in the log directory.

</ApiMember>

### `get_global_stats_log_path` {#airbyte.logs.get_global_stats_log_path}

<ApiMember kind="function">

<ApiSignature>

```python
def get_global_stats_log_path() -> pathlib.Path | None
```

</ApiSignature>

Return the path to the performance log file.

</ApiMember>

### `get_global_stats_logger` {#airbyte.logs.get_global_stats_logger}

<ApiMember kind="function">

<ApiSignature>

```python
def get_global_stats_logger() -> structlog._generic.BoundLogger
```

</ApiSignature>

Create a stats logger for performance metrics.

</ApiMember>

### `new_passthrough_file_logger` {#airbyte.logs.new_passthrough_file_logger}

<ApiMember kind="function">

<ApiSignature>

```python
def new_passthrough_file_logger(connector_name: str) -> logging.Logger
```

</ApiSignature>

Create a logger from logging module.

</ApiMember>

### `warn_once` {#airbyte.logs.warn_once}

<ApiMember kind="function">

<ApiSignature>

```python
def warn_once(
    message: str,
    logger: logging.Logger | None = None,
    *,
    with_stack: int | bool,
) -> None
```

</ApiSignature>

Emit a warning message only once.

This function is a wrapper around the `warnings.warn` function that logs the warning message
to the global logger. The warning message is only emitted once per unique message.

</ApiMember>