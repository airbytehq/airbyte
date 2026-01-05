---
sidebar_label: base
title: airbyte._executors.base
---

## annotations

## subprocess

## ABC

## abstractmethod

## contextmanager

## Event

## Thread

## IO

## TYPE\_CHECKING

## Any

## cast

## exc

## AirbyteMessageIterator

#### \_LATEST\_VERSION

## ExceptionHolder Objects

```python
class ExceptionHolder()
```

#### \_\_init\_\_

```python
def __init__() -> None
```

#### set\_exception

```python
def set_exception(ex: Exception) -> None
```

#### \_pump\_input

```python
def _pump_input(pipe: IO[str], messages: AirbyteMessageIterator,
                exception_holder: ExceptionHolder) -> None
```

Pump lines into a pipe.

#### \_stream\_from\_file

```python
def _stream_from_file(file: IO[str]) -> Generator[str, Any, None]
```

Stream lines from a file.

#### \_stream\_from\_subprocess

```python
@contextmanager
def _stream_from_subprocess(
        args: list[str],
        *,
        stdin: IO[str] | AirbyteMessageIterator | None = None,
        log_file: IO[str] | None = None,
        suppress_stderr: bool = False) -> Generator[Iterable[str], None, None]
```

Stream lines from a subprocess.

When stdin is an AirbyteMessageIterator, input is pumped to the subprocess
in a separate thread while output is read concurrently. This avoids a
potential deadlock where the subprocess blocks on stdout (buffer full)
while we&#x27;re waiting for input to finish before reading stdout.

## Executor Objects

```python
class Executor(ABC)
```

#### \_\_init\_\_

```python
def __init__(*,
             name: str | None = None,
             metadata: ConnectorMetadata | None = None,
             target_version: str | None = None) -> None
```

Initialize a connector executor.

The &#x27;name&#x27; param is required if &#x27;metadata&#x27; is None.

#### \_cli

```python
@property
@abstractmethod
def _cli() -> list[str]
```

Get the base args of the CLI executable.

Args will be appended to this list.

#### map\_cli\_args

```python
def map_cli_args(args: list[str]) -> list[str]
```

Map CLI args if needed.

By default, this is a no-op. Subclasses may override this method in order to
map CLI args into the format expected by the connector.

#### execute

```python
def execute(args: list[str],
            *,
            stdin: IO[str] | AirbyteMessageIterator | None = None,
            suppress_stderr: bool = False) -> Iterator[str]
```

Execute a command and return an iterator of STDOUT lines.

If stdin is provided, it will be passed to the subprocess as STDIN.
If suppress_stderr is True, stderr output will be suppressed to reduce noise.

#### ensure\_installation

```python
@abstractmethod
def ensure_installation(*, auto_fix: bool = True) -> None
```

#### install

```python
@abstractmethod
def install() -> None
```

#### uninstall

```python
@abstractmethod
def uninstall() -> None
```

#### get\_installed\_version

```python
def get_installed_version(*,
                          raise_on_error: bool = False,
                          recheck: bool = False) -> str | None
```

Detect the version of the connector installed.

