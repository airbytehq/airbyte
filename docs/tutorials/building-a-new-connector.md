---
description: Building a toy source connector to illustrate Airbyte's main concepts  
---

# Build a new connector

This tutorial walks you through building a very simple Airbyte source to demonstrate the following concepts in Action: 
* [The Airbyte Specification](../architecture/airbyte-specification.md) and the interface implemented by a source connector
* [Packaging your connector](../contributing-to-airbyte/building-new-connector/README.md#1-implement--package-the-connector) 
* [Testing your connector](../contributing-to-airbyte/building-new-connector/testing-connectors.md)
* [Adding incremental sync to your connector](../architecture/incremental.md)

We intentionally don't use helper libraries provided by Airbyte so that this tutorial is self-contained. If you were building a "real" source, 
you'll want to use the helper modules provided by Airbyte. We'll mention those at the very end. For now, let's get started.

## Our connector: a stock ticker API
Our connector will output the daily price of a stock since a given date. We'll leverage the free [IEX Cloud API](https://iexcloud.io/docs/api/) for this.
We'll use Python to implement the connector because its syntax is accessible to most programmers, but the process described here can be applied 
to any language.  

Here's the outline of what we'll do to build our connector:
1. Use the Airbyte connector template to bootstrap the connector package
2. Implement the 4 methods required by the Airbyte Specification
3. Package the connector in a Docker image
4. Test the connector using Airbyte's Standard Test Suite
5. Use the connector to run a sync from the Airbyte UI 

Once we've completed the above steps, we will have built a functioning connector. Then, we'll add some optional functionality: 
6. Support [incremental sync](../architecture/incremental.md) 
7. Add custom integration tests

### 1. Bootstrap the connector package
We'll start the process from the Airbyte repository root: 

```

```
First, let's create a new branch 

Airbyte provides a code generator which bootstraps the scaffolding for our connector. To use it, run the following from the repo :
```
cd airbyte-integrations/connector-templates/generator
# You'll need to have NPM installed. See https://www.npmjs.com/get-npm for more information
npm install
npm run generate
```

We'll select the generic template and call the connector `stock-ticker`: 

```

```

Note that if you were developing a "real" Python connector, you should use the Python generator to automatically get the Airbyte Python helpers.

