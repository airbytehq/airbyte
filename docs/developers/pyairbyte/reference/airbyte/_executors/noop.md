---
sidebar_label: noop
title: airbyte._executors.noop
---

NoOp executor for connectors that don&#x27;t require local execution.

## annotations

## json

## logging

## TYPE\_CHECKING

## Any

## exc

## Executor

## get\_connector\_spec\_from\_registry

#### logger

## NoOpExecutor Objects

```python
class NoOpExecutor(Executor)
```

Executor that fetches specs from registry without local installation.

This executor is useful for scenarios where you need to validate connector
configurations but don&#x27;t need to actually run the connector locally (e.g.,
when deploying to Airbyte Cloud).

The NoOpExecutor:
- Fetches connector specs from the Airbyte registry
- Supports the &#x27;spec&#x27; command for configuration validation
- Does not support execution commands (check, discover, read, write)
- Does not require Docker or Python installation

#### \_\_init\_\_

```python
def __init__(*,
             name: str | None = None,
             metadata: ConnectorMetadata | None = None,
             target_version: str | None = None) -> None
```

Initialize the NoOp executor.

#### \_cli

```python
@property
def _cli() -> list[str]
```

Return a placeholder CLI command.

This is never actually used since execute() is overridden.

#### execute

```python
def execute(args: list[str],
            *,
            stdin: IO[str] | AirbyteMessageIterator | None = None,
            suppress_stderr: bool = False) -> Iterator[str]
```

Execute a command and return an iterator of STDOUT lines.

Only the &#x27;spec&#x27; command is supported. Other commands will raise an error.

#### ensure\_installation

```python
def ensure_installation(*, auto_fix: bool = True) -> None
```

No-op: NoOpExecutor doesn&#x27;t require installation.

#### install

```python
def install() -> None
```

No-op: NoOpExecutor doesn&#x27;t require installation.

#### uninstall

```python
def uninstall() -> None
```

No-op: NoOpExecutor doesn&#x27;t manage installations.

#### \_\_all\_\_

