---
sidebar_label: logs
title: airbyte.logs
---

PyAirbyte Logging features and related configuration.

By default, PyAirbyte main logs are written to a file in the `AIRBYTE_LOGGING_ROOT` directory, which
defaults to a system-created temporary directory. PyAirbyte also maintains connector-specific log
files within the same directory, under a subfolder with the name of the connector.

PyAirbyte supports structured JSON logging, which is disabled by default. To enable structured
logging in JSON, set `AIRBYTE_STRUCTURED_LOGGING` to `True`.

## annotations

## logging

## os

## platform

## sys

## tempfile

## warnings

## lru\_cache

## Path

## structlog

## ulid

## ab\_datetime\_now

#### \_str\_to\_bool

```python
def _str_to_bool(value: str) -> bool
```

Convert a string value of an environment values to a boolean value.

#### AIRBYTE\_STRUCTURED\_LOGGING

Whether to enable structured logging.

This value is read from the `AIRBYTE_STRUCTURED_LOGGING` environment variable. If the variable is
not set, the default value is `False`.

#### \_warned\_messages

#### warn\_once

```python
def warn_once(message: str,
              logger: logging.Logger | None = None,
              *,
              with_stack: int | bool) -> None
```

Emit a warning message only once.

This function is a wrapper around the `warnings.warn` function that logs the warning message
to the global logger. The warning message is only emitted once per unique message.

#### \_get\_logging\_root

```python
def _get_logging_root() -> Path | None
```

Return the root directory for logs.

Returns `None` if no valid path can be found.

This is the directory where logs are stored.

#### AIRBYTE\_LOGGING\_ROOT

The root directory for Airbyte logs.

This value can be overridden by setting the `AIRBYTE_LOGGING_ROOT` environment variable.

If not provided, PyAirbyte will use `/tmp/airbyte/logs/` where `/tmp/` is the OS&#x27;s default
temporary directory. If the directory cannot be created, PyAirbyte will log a warning and
set this value to `None`.

#### get\_global\_file\_logger

```python
@lru_cache
def get_global_file_logger() -> logging.Logger | None
```

Return the global logger for PyAirbyte.

This logger is configured to write logs to the console and to a file in the log directory.

#### get\_global\_stats\_log\_path

```python
def get_global_stats_log_path() -> Path | None
```

Return the path to the performance log file.

#### get\_global\_stats\_logger

```python
@lru_cache
def get_global_stats_logger() -> structlog.BoundLogger
```

Create a stats logger for performance metrics.

#### new\_passthrough\_file\_logger

```python
def new_passthrough_file_logger(connector_name: str) -> logging.Logger
```

Create a logger from logging module.

