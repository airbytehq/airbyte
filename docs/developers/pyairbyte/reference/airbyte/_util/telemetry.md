---
sidebar_label: telemetry
title: airbyte._util.telemetry
---

Telemetry implementation for PyAirbyte.

We track some basic telemetry to help us understand how PyAirbyte is used. You can opt-out of
telemetry at any time by setting the environment variable DO_NOT_TRACK to any value.

If you are able to provide telemetry, it is greatly appreciated. Telemetry helps us understand how
the library is used, what features are working. We also use this telemetry to prioritize bug fixes
and improvements to the connectors themselves, focusing first on connectors that are (1) most used
and (2) report the most sync failures as a percentage of total attempted syncs.

Your privacy and security are our priority. We do not track any PII (personally identifiable
information), nor do we track anything that _could_ contain PII without first hashing the data
using a one-way hash algorithm. We only track the minimum information necessary to understand how
PyAirbyte is used, and to dedupe users to determine how many users or use cases there are.


Here is what is tracked:
- The version of PyAirbyte.
- The Python version.
- The OS.
- The source type (venv or local install).
- The source name and version number.
- The state of the sync (started, failed, succeeded).
- The cache type (Snowflake, Postgres, etc.).
- The number of records processed.
- The application hash, which is a hash of either the notebook name or Python script name.
- Flags to help us understand if PyAirbyte is running on CI, Google Colab, or another environment.

## annotations

## datetime

## os

## suppress

## Enum

## lru\_cache

## Path

## Any

## cast

## requests

## ulid

## yaml

## exc

## meta

## ConnectorRuntimeInfo

## WriterRuntimeInfo

## one\_way\_hash

## AIRBYTE\_OFFLINE\_MODE

## get\_version

#### DEBUG

Enable debug mode for telemetry code.

#### PYAIRBYTE\_APP\_TRACKING\_KEY

This key corresponds globally to the &quot;PyAirbyte&quot; application.

#### PYAIRBYTE\_SESSION\_ID

Unique identifier for the current invocation of PyAirbyte.

This is used to determine the order of operations within a specific session.
It is not a unique identifier for the user.

#### DO\_NOT\_TRACK

Environment variable to opt-out of telemetry.

#### \_ENV\_ANALYTICS\_ID

Allows user to override the anonymous user ID

#### \_ANALYTICS\_FILE

#### \_ANALYTICS\_ID

#### UNKNOWN

#### \_setup\_analytics

```python
def _setup_analytics() -> str | bool
```

Set up the analytics file if it doesn&#x27;t exist.

Return the anonymous user ID or False if the user has opted out.

#### \_get\_analytics\_id

```python
def _get_analytics_id() -> str | None
```

#### \_ANALYTICS\_ID

## EventState Objects

```python
class EventState(str, Enum)
```

#### STARTED

#### FAILED

#### SUCCEEDED

#### CANCELED

## EventType Objects

```python
class EventType(str, Enum)
```

#### INSTALL

#### SYNC

#### VALIDATE

#### CHECK

#### get\_env\_flags

```python
@lru_cache
def get_env_flags() -> dict[str, Any]
```

#### send\_telemetry

```python
def send_telemetry(*,
                   source: ConnectorRuntimeInfo | None,
                   destination: ConnectorRuntimeInfo | None,
                   cache: WriterRuntimeInfo | None,
                   state: EventState,
                   event_type: EventType,
                   number_of_records: int | None = None,
                   exception: Exception | None = None) -> None
```

#### log\_config\_validation\_result

```python
def log_config_validation_result(name: str,
                                 state: EventState,
                                 exception: Exception | None = None) -> None
```

Log a config validation event.

If the name starts with &quot;destination-&quot;, it is treated as a destination name. Otherwise, it is
treated as a source name.

#### log\_connector\_check\_result

```python
def log_connector_check_result(name: str,
                               state: EventState,
                               exception: Exception | None = None) -> None
```

Log a connector `check` result.

If the name starts with &quot;destination-&quot;, it is treated as a destination name. Otherwise, it is
treated as a source name.

#### log\_install\_state

```python
def log_install_state(name: str,
                      state: EventState,
                      exception: Exception | None = None) -> None
```

Log an install event.

