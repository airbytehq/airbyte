---
sidebar_label: text_util
title: airbyte._util.text_util
---

Utility functions for working with text.

## annotations

## ulid

#### generate\_ulid

```python
def generate_ulid() -> str
```

Generate a new ULID.

#### generate\_random\_suffix

```python
def generate_random_suffix() -> str
```

Generate a random suffix for use in temporary names.

By default, this function generates a ULID and returns a 9-character string
which will be monotonically sortable. It is not guaranteed to be unique but
is sufficient for small-scale and medium-scale use cases.

