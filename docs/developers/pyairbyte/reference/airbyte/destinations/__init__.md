---
sidebar_label: destinations
title: airbyte.destinations
---

Destinations module.

This module contains classes and methods for interacting with Airbyte destinations. You can use this
module to create custom destinations, or to interact with existing destinations.

## Getting Started

To get started with destinations, you can use the `get_destination()` method to create a destination
object. This method takes a destination name and configuration, and returns a destination object
that you can use to write data to the destination.


## Writing Data to a Destination

To write data to a destination, you can use the `Destination.write()` method. This method
takes either a `airbyte.Source` or `airbyte.ReadResult` object.

## Writing to a destination from a source

To write directly from a source, simply pass the source object to the `Destination.write()` method:


## Writing from a read result:

To write from a read result, you can use the following pattern. First, read data from the source,
then write the data to the destination, using the `ReadResult` object as a buffer between the source
and destination:


## Using Docker and Python-based Connectors

By default, the `get_destination()` method will look for a Python-based connector. If you want to
use a Docker-based connector, you can set the `docker_image` parameter to `True`:


**Note:** Unlike source connectors, most destination connectors are written in Java, and for this
reason are only available as Docker-based connectors. If you need to load to a SQL database and your
runtime does not support docker, you may want to use the `airbyte.caches` module to load data to
a SQL cache. Caches are mostly identical to destinations in behavior, and are implemented internally
to PyAirbyte so they can run anywhere that PyAirbyte can run.
`Destination.write()`0
`Destination.write()`1
`Destination.write()`2
`Destination.write()`3

## annotations

## TYPE\_CHECKING

## Destination

## get\_destination

## get\_noop\_destination

#### \_\_all\_\_

