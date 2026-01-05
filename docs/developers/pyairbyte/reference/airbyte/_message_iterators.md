---
sidebar_label: _message_iterators
title: airbyte._message_iterators
---

Message generator for Airbyte messages.

## annotations

## sys

## Iterator

## IO

## TYPE\_CHECKING

## cast

## pydantic

## final

## ab\_datetime\_now

## AirbyteMessage

## AirbyteRecordMessage

## AirbyteStreamStatus

## AirbyteStreamStatusTraceMessage

## AirbyteTraceMessage

## StreamDescriptor

## TraceType

## Type

## AB\_EXTRACTED\_AT\_COLUMN

#### \_new\_stream\_success\_message

```python
def _new_stream_success_message(stream_name: str) -> AirbyteMessage
```

Return a new stream success message.

## AirbyteMessageIterator Objects

```python
class AirbyteMessageIterator()
```

Abstract base class for Airbyte message iterables.

This class behaves like Iterator[AirbyteMessage] but it can also be used
as IO[str]. In the latter case, it will return the JSON string representation of
the all messages in the iterator.

#### \_\_init\_\_

```python
def __init__(iterable: Iterable[AirbyteMessage]) -> None
```

#### \_\_iter\_\_

```python
@final
def __iter__() -> Iterator[AirbyteMessage]
```

The class itself is not a iterator but this method makes it iterable.

#### \_\_next\_\_

```python
@final
def __next__() -> AirbyteMessage
```

Delegate to the internal iterator.

#### read

```python
@final
def read() -> str
```

Read the next message from the iterator.

#### from\_read\_result

```python
@classmethod
def from_read_result(cls, read_result: ReadResult) -> AirbyteMessageIterator
```

Create a iterator from a `ReadResult` object.

#### from\_str\_buffer

```python
@classmethod
def from_str_buffer(cls, buffer: IO[str]) -> AirbyteMessageIterator
```

Create a iterator that reads messages from a buffer.

#### from\_str\_iterable

```python
@classmethod
def from_str_iterable(cls, buffer: Iterable[str]) -> AirbyteMessageIterator
```

Yields AirbyteMessage objects read from STDIN.

#### from\_stdin

```python
@classmethod
def from_stdin(cls) -> AirbyteMessageIterator
```

Create an iterator that reads messages from STDIN.

#### from\_files

```python
@classmethod
def from_files(
        cls, file_iterator: Iterator[Path],
        file_opener: Callable[[Path], IO[str]]) -> AirbyteMessageIterator
```

Create an iterator that reads messages from a file iterator.

