# Firebolt Source

## Overview

Firebolt is a cloud data warehouse purpose-built to provide sub-second analytics performance on massive, terabyte-scale data sets. 

Firebolt has two main concepts: Databases, which denote the storage of data and Engines, which describe the compute layer on top of a Database.

Firebolt has three types of tables: External, Fact and Dimension. External tables, which represent a raw file structure in storage. Dimension tables, which are optimised for fetching and store data on each node in an Engine. Fact tables are similar to Dimension, but they shard the data across the nodes. The usual workload is to write source data into a set of files on S3, wrap them with an External table and write this data to a fetch-optimised Fact or Dimension table.

## Connector

Firebolt is a data warehouse so the most efficient way to write data into it would be in bulk. Firebolt connector offers two ways of writing data: SQL and S3. SQL transfers data in small batches and is most useful for prototyping. S3 buffers data on Amazon S3 storage and persists the data to Firebolt at the end of execution. The latter is the most efficient way of loading data, but it requires AWS S3 access.

This connector uses [firebolt-sdk](https://pypi.org/project/firebolt-sdk/), which is a [PEP-249](https://peps.python.org/pep-0249/) DB API implementation.
`Connection` object is used to connect to a specified Engine, wich runs subsequent queries against the data stored in the Database using the `Cursor` object.
[Pyarrow](https://pypi.org/project/pyarrow/) is used to efficiently store and upload data to S3.

## Notes

* Integration testing requires the user to have a running engine. Spinning up an engine can take a while so this ensures a faster iteration on the connector.
* S3 is generally faster writing strategy and should be preferred.