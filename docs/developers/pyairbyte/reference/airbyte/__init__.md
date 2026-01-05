---
sidebar_label: airbyte
title: airbyte
---

***PyAirbyte brings the power of Airbyte to every Python developer.***

[![PyPI version](https://badge.fury.io/py/airbyte.svg)](https://badge.fury.io/py/airbyte)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/airbyte)](https://pypi.org/project/airbyte/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airbyte)](https://pypi.org/project/airbyte/)
[![Star on GitHub](https://img.shields.io/github/stars/airbytehq/pyairbyte.svg?style=social&amp;label=★%20on%20GitHub)](https://github.com/airbytehq/pyairbyte)

# Getting Started

## Reading Data

You can connect to any of [hundreds of sources](https://docs.airbyte.com/integrations/sources/)
using the `get_source` method. You can then read data from sources using `Source.read` method.


For more information, see the `airbyte.sources` module.

## Writing to SQL Caches

Data can be written to caches using a number of SQL-based cache implementations, including
Postgres, BigQuery, Snowflake, DuckDB, and MotherDuck. If you do not specify a cache, PyAirbyte
will automatically use a local DuckDB cache by default.

For more information, see the `airbyte.caches` module.

## Writing to Destination Connectors

Data can be written to destinations using the `Destination.write` method. You can connect to
destinations using the `get_destination` method. PyAirbyte supports all Airbyte destinations, but
Docker is required on your machine in order to run Java-based destinations.

**Note:** When loading to a SQL database, we recommend using SQL cache (where available,
[see above](#writing-to-sql-caches)) instead of a destination connector. This is because SQL caches
are Python-native and therefor more portable when run from different Python-based environments which
might not have Docker container support. Destinations in PyAirbyte are uniquely suited for loading
to non-SQL platforms such as vector stores and other reverse ETL-type use cases.

For more information, see the `airbyte.destinations` module and the full list of destination
connectors [here](https://docs.airbyte.com/integrations/destinations/).

# PyAirbyte API

## Importing as `ab`

Most examples in the PyAirbyte documentation use the `import airbyte as ab` convention. The `ab`
alias is recommended, making code more concise and readable. When getting started, this
also saves you from digging in submodules to find the classes and functions you need, since
frequently-used classes and functions are available at the top level of the `Source.read`0 module.

## Navigating the API

While many PyAirbyte classes and functions are available at the top level of the `Source.read`0 module,
you can also import classes and functions from submodules directly. For example, while you can
import the `Source.read`2 class from `Source.read`0, you can also import it from the `Source.read`4 submodule like
this:


Whether you import from the top level or from a submodule, the classes and functions are the same.
We expect that most users will import from the top level when getting started, and then import from
submodules when they are deploying more complex implementations.

For quick reference, top-Level modules are listed in the left sidebar of this page.

# Other Resources

- [PyAirbyte GitHub Readme](https://github.com/airbytehq/pyairbyte)
- [PyAirbyte Issue Tracker](https://github.com/airbytehq/pyairbyte/issues)
- [Frequently Asked Questions](https://github.com/airbytehq/PyAirbyte/blob/main/docs/faq.md)
- [PyAirbyte Contributors Guide](https://github.com/airbytehq/PyAirbyte/blob/main/docs/CONTRIBUTING.md)
- [GitHub Releases](https://github.com/airbytehq/PyAirbyte/releases)

----------------------

# API Reference

Below is a list of all classes, functions, and modules available in the top-level `Source.read`0
module. (This is a long list!) If you are just starting out, we recommend beginning by selecting a
submodule to navigate to from the left sidebar or from the list below:

Each module
has its own documentation and code samples related to effectively using the related capabilities.

- **`Source.read`6** - Working with Airbyte Cloud, including running jobs remotely.
- **`airbyte.caches`** - Working with caches, including how to inspect a cache and get data from it.
- **`Source.read`8** - Working with datasets, including how to read from datasets and convert to
other formats, such as Pandas, Arrow, and LLM Document formats.
- **`airbyte.destinations`** - Working with destinations, including how to write to Airbyte
destinations connectors.
- **`airbyte.sources`0** - Working with LLM documents, including how to convert records into
document formats, for instance, when working with AI libraries like LangChain.
- **`airbyte.sources`1** - Definitions of all exception and warning classes used in PyAirbyte.
- **`airbyte.sources`2** - Experimental features and utilities that do not yet have a stable
API.
- **`airbyte.sources`3** - Logging functionality and configuration.
- **`airbyte.sources`4** - Internal record handling classes.
- **`airbyte.sources`5** - Documents the classes returned when working with results from
`Source.read` and `Destination.write`
- **`airbyte.sources`8** - Tools for managing secrets in PyAirbyte.
- **`airbyte.sources`** - Tools for creating and reading from Airbyte sources. This includes
`airbyte.caches`0 to declare a source, `airbyte.caches`1 for reading data,
and `airbyte.caches`2 to peek at records without caching or writing them
directly.

----------------------
`airbyte.caches`3
`airbyte.caches`4

## annotations

## TYPE\_CHECKING

## registry

## BigQueryCache

## DuckDBCache

## get\_colab\_cache

## get\_default\_cache

## new\_local\_cache

## CachedDataset

## Destination

## get\_destination

## StreamRecord

## get\_available\_connectors

## ReadResult

## WriteResult

## SecretSourceEnum

## get\_secret

## Source

## get\_source

#### \_\_all\_\_

#### \_\_docformat\_\_

