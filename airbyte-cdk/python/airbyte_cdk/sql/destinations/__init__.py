# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Destinations module.

This module contains classes and methods for interacting with Airbyte destinations. You can use this
module to create custom destinations, or to interact with existing destinations.

## Getting Started

To get started with destinations, you can use the `get_destination()` method to create a destination
object. This method takes a destination name and configuration, and returns a destination object
that you can use to write data to the destination.

```python
import airbyte as ab

my_destination = ab.get_destination(
    "destination-foo",
    config={"api_key": "my_api_key"},
    docker_image=True,
)
```

## Writing Data to a Destination

To write data to a destination, you can use the `Destination.write()` method. This method
takes either a `airbyte.Source` or `airbyte.ReadResult` object.

## Writing to a destination from a source

To write directly from a source, simply pass the source object to the `Destination.write()` method:

```python
my_source = get_source(...)
my_destination = get_destination(...)
my_destination.write(source_faker)
```

## Writing from a read result:

To write from a read result, you can use the following pattern. First, read data from the source,
then write the data to the destination, using the `ReadResult` object as a buffer between the source
and destination:

```python
# First read data from the source:
my_source = get_source(...)
read_result = my_source.read(...)

# Optionally, you can validate data before writing it:
# ...misc validation code here...

# Then write the data to the destination:
my_destination.write(read_result)
```

## Using Docker and Python-based Connectors

By default, the `get_destination()` method will look for a Python-based connector. If you want to
use a Docker-based connector, you can set the `docker_image` parameter to `True`:

```python
my_destination = ab.get_destination(
    "destination-foo",
    config={"api_key": "my_api_key"},
    docker_image=True,
)
```

**Note:** Unlike source connectors, most destination connectors are written in Java, and for this
reason are only available as Docker-based connectors. If you need to load to a SQL database and your
runtime does not support docker, you may want to use the `airbyte.caches` module to load data to
a SQL cache. Caches are mostly identical to destinations in behavior, and are implemented internally
to Airbyte so they can run anywhere that Airbyte can run.
"""

from __future__ import annotations

from airbyte_cdk.sql.destinations import util
from airbyte_cdk.sql.destinations.base import Destination
from airbyte_cdk.sql.destinations.util import (
    get_destination,
    get_noop_destination,
)


__all__ = [
    # Modules
    "util",
    # Methods
    "get_destination",
    "get_noop_destination",
    # Classes
    "Destination",
]
