# Firebolt Source

## Overview

Firebolt is a cloud data warehouse purpose-built to provide sub-second analytics performance on massive, terabyte-scale data sets.

Firebolt has two main concepts: Databases, which denote the storage of data and Engines, which describe the compute layer on top of a Database.

Firebolt has three types of tables: External, Fact and Dimension. External tables, which represent a raw file structure in storage. Dimension tables, which are optimised for fetching and store data on each node in an Engine. Fact tables are similar to Dimension, but they shard the data across the nodes. The usual workload is to write source data into a set of files on S3, wrap them with an External table and write this data to a fetch-optimised Fact or Dimension table.

## Connector

This connector uses [firebolt-sdk](https://pypi.org/project/firebolt-sdk/), which is a [PEP-249](https://peps.python.org/pep-0249/) DB API implementation.
`Connection` object is used to connect to a specified Engine, wich runs subsequent queries against the data stored in the Database using the `Cursor` object.

## Notes

- External tables are not available as a source for performance reasons.
- Only Full reads are supported for now.
- Integration/Acceptance testing requires the user to have a running engine. Spinning up an engine can take a while so this ensures a faster iteration on the connector.
- Pagination is not available at the moment so large enough data sets might cause out of memory errors
