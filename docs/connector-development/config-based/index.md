# Getting Started with Low-Code CDK

:warning: This framework is in [alpha](https://docs.airbyte.com/project-overview/product-release-stages/#alpha). It is still in active development and may include backward-incompatible changes. Please share feedback and requests directly with us at feedback@airbyte.io :warning:

## From scratch

This section gives an overview of the low-code framework.

- [Overview](overview.md)
- [YAML structure](yaml-structure.md)
- [Reference docs](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.html)

## Concepts

This section contains additional information on the different components that can be used to define a low-code connector.

- [Authentication](authentication.md)
- [Error handling](error-handling.md)
- [Pagination](pagination.md)
- [Record selection](record-selector.md)
- [Request options](request-options.md)
- [Stream slicers](stream-slicers.md)
- [Substreams](substreams.md)

## Tutorial

This section a tutorial that will guide you through the end-to-end process of implementing a low-code connector.

0. [Getting started](tutorial/0-getting-started.md)
1. [Creating a source](tutorial/1-create-source.md)
2. [Installing dependencies](tutorial/2-install-dependencies.md)
3. [Connecting to the API](tutorial/3-connecting-to-the-API-source.md)
4. [Reading data](tutorial/4-reading-data.md)
5. [Incremental reads](tutorial/5-incremental-reads.md)
6. [Testing](tutorial/6-testing.md)
