---
id: airbyte-logs
title: airbyte.logs
---

Module airbyte.logs
===================
PyAirbyte Logging features and related configuration.

By default, PyAirbyte main logs are written to a file in the `AIRBYTE_LOGGING_ROOT` directory, which
defaults to a system-created temporary directory. PyAirbyte also maintains connector-specific log
files within the same directory, under a subfolder with the name of the connector.

PyAirbyte supports structured JSON logging, which is disabled by default. To enable structured
logging in JSON, set `AIRBYTE_STRUCTURED_LOGGING` to `True`.

Variables
---------

`AIRBYTE_LOGGING_ROOT: pathlib.Path | None`
:   The root directory for Airbyte logs.
    
    This value can be overridden by setting the `AIRBYTE_LOGGING_ROOT` environment variable.
    
    If not provided, PyAirbyte will use `/tmp/airbyte/logs/` where `/tmp/` is the OS's default
    temporary directory. If the directory cannot be created, PyAirbyte will log a warning and
    set this value to `None`.

`AIRBYTE_STRUCTURED_LOGGING: bool`
:   Whether to enable structured logging.
    
    This value is read from the `AIRBYTE_STRUCTURED_LOGGING` environment variable. If the variable is
    not set, the default value is `False`.

Functions
---------

`get_global_file_logger() ‑> logging.Logger | None`
:   Return the global logger for PyAirbyte.
    
    This logger is configured to write logs to the console and to a file in the log directory.

`get_global_stats_log_path() ‑> pathlib.Path | None`
:   Return the path to the performance log file.

`get_global_stats_logger() ‑> structlog._generic.BoundLogger`
:   Create a stats logger for performance metrics.

`new_passthrough_file_logger(connector_name: str) ‑> logging.Logger`
:   Create a logger from logging module.

`warn_once(message: str, logger: logging.Logger | None = None, *, with_stack: int | bool) ‑> None`
:   Emit a warning message only once.
    
    This function is a wrapper around the `warnings.warn` function that logs the warning message
    to the global logger. The warning message is only emitted once per unique message.