---
sidebar_label: api_duck_types
title: airbyte._util.api_duck_types
---

A set of duck-typed classes for working with the Airbyte API.

## annotations

## TYPE\_CHECKING

## Protocol

## AirbyteApiResponseDuckType Objects

```python
class AirbyteApiResponseDuckType(Protocol)
```

Used for duck-typing various Airbyte API responses.

#### content\_type

HTTP response content type for this operation

#### status\_code

HTTP response status code for this operation

#### raw\_response

Raw HTTP response; suitable for custom response parsing

