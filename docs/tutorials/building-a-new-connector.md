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
2. Implement the methods required by the Airbyte Specification for our connector:
    1. `spec`: declares the user-provided credentials or configuration needed to run the connector
    2. `check`: tests if the user-provided configuration is valid and can be used to run the connector
    3. `discover`: declares the different streams of data that this connector can output
    4. `read`: reads data from the underlying data source (The stock ticker API) 
3. Package the connector in a Docker image
4. Test the connector using Airbyte's Standard Test Suite
5. Use the connector to run a sync from the Airbyte UI 

Once we've completed the above steps, we will have built a functioning connector. Then, we'll add some optional functionality: 
6. Support [incremental sync](../architecture/incremental.md) 
7. Add custom integration tests

### 1. Bootstrap the connector package
We'll start the process from the Airbyte repository root: 

```shell script
$ pwd
/Users/sherifnada/code/airbyte
```

First, let's create a new branch:
```shell script
$ git checkout -b $(whoami)/source-connector-tutorial
Switched to a new branch 'sherifnada/source-connector-tutorial'
```
 
Airbyte provides a code generator which bootstraps the scaffolding for our connector. Let's use it by running:
```shell script
$ cd airbyte-integrations/connector-templates/generator
# Install NPM from https://www.npmjs.com/get-npm if you don't have it
$ npm install
$ npm run generate
```

We'll select the generic template and call the connector `stock-ticker-api`: 
![](../.gitbook/assets/newsourcetutorial_plop.gif)

Note that if you were developing a "real" Python connector, you should use the Python generator to automatically get the Airbyte Python helpers.

Head to the connector directory and we should see the following files have been generated: 
```shell script
$ cd ../../connectors/source-stock-ticker-api
ls
Dockerfile              NEW_SOURCE_CHECKLIST.md              build.gradle
```

We'll use each of these files later. But first, let's write some code!

### 2. Implement the connector in line with the Airbyte Specification
In the connector package directory, create a single python file `source.py` that will hold our implementation:
```shell script
$ touch source.py
```                                                                                    

#### Implement the spec operation
At this stage in the tutorial, we just want to implement the `spec` operation. This involves a couple of steps: 
1. Decide which inputs we need from the user in order to connect to the stock ticker API i.e: the connector's specification, and encode it as a JSON file. 
2. Identify when the connector has been invoked with the `spec` operation and return the specification as an `AirbyteMessage` 

To contact the stock ticker API, we need two things: 
1. Which stock ticker we're interested in
2. The API key to use when contacting the API (you can obtain a free API key from [IEX Cloud](https://iexcloud.io/docs/api)'s free plan)

Let's create a [JsonSchema](http://json-schema.org/) file `spec.json` encoding these two requirements: 

```json
{
  "documentationUrl": "https://iexcloud.io/docs/api",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["stock_ticker", "api_key"],
    "additionalProperties": false,
    "properties": {
      "stock_ticker": {
        "type": "string",
        "title": "Stock Ticker",
        "description": "The stock ticker to track",
        "examples": ["AAPL", "TSLA", "AMZN"]
      },
      "api_key": {
        "type": "string",
        "description": "The IEX Cloud API key to use to hit the API.",
        "airbyte_secret": true
      }
    }
  }
}
```

* `documentationUrl` is the URL that will appear in the UI for the user to gain more info about this connector. Typically this points to `docs.airbyte.io/integrations/sources/source-<connector_name>` but to keep things simple we won't show adding documentation.
* `title` is the "human readable" title displayed in the UI. Without this field, The Stock Ticker field will have the title `stock_ticker` in the UI
* `description` will be shown in the Airbyte UI under each field to help the user understand it   
* `airbyte_secret` used by Airbyte to determine if the field should be displayed as a password (e.g: `********`) in the UI and not readable from the API. 

We'll save this file in the root directory of our connector. Now we have the following files: 
```shell script
$ ls -1
Dockerfile
NEW_SOURCE_CHECKLIST.md
build.gradle
source.py
spec.json
```

Now, let's edit `source.py` to detect if the program was invoked with the `spec` argument and if so, output the connector specification 

```python
# source.py
import argparse # import a library to help us parse arguments 



```
