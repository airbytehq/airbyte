---
description: Building a toy source connector to illustrate Airbyte's main concepts
---

# Building a Toy Connector

This tutorial walks you through building a simple Airbyte source to demonstrate the following concepts in Action:

* [The Airbyte Specification](../architecture/airbyte-specification.md) and the interface implemented by a source connector
* [The AirbyteCatalog](beginners-guide-to-catalog.md)
* [Packaging your connector](../contributing-to-airbyte/building-new-connector/#1-implement--package-the-connector)
* [Testing your connector](../contributing-to-airbyte/building-new-connector/testing-connectors.md)

At the end of this tutorial, you will have a working source that you will be able to use in the Airbyte UI.

We intentionally don't use helper libraries provided by Airbyte so that this tutorial is self-contained. If you were building a "real" source, you'll want to use the helper modules provided by Airbyte. We'll mention those at the very end. For now, let's get started.

This tutorial can be done entirely on your local workstation.

### Requirements

To run this tutorial, you'll need:

* Docker, Python, and Java with the versions listed in the [tech stack section](../architecture/tech-stack.md).
* The `requests` Python package installed via `pip install requests` \(or `pip3` if `pip` is linked to a Python2 installation on your system\)

**A note on running Python**: all the commands below assume that `python` points to a version of python 3. Verify this by running

```bash
$ python --version
Python 3.7.9
```

On some systems, `python` points to a Python2 installation and `python3` points to Python3. If this is the case on your machine, substitute all `python` commands in this guide with `python3` . Otherwise, make sure to install Python 3 before beginning.

## Our connector: a stock ticker API

Our connector will output the daily price of a stock since a given date. We'll leverage the free [IEX Cloud API](https://iexcloud.io/pricing/) for this \(the free account is at the bottom\). We'll use Python to implement the connector because its syntax is accessible to most programmers, but the process described here can be applied to any language.

Here's the outline of what we'll do to build our connector:

1. Use the Airbyte connector template to bootstrap the connector package
2. Implement the methods required by the Airbyte Specification for our connector:
   1. `spec`: declares the user-provided credentials or configuration needed to run the connector
   2. `check`: tests if with the user-provided configuration the connector can connect with the underlying data source.
   3. `discover`: declares the different streams of data that this connector can output
   4. `read`: reads data from the underlying data source \(The stock ticker API\)
3. Package the connector in a Docker image
4. Test the connector using Airbyte's Standard Test Suite
5. Use the connector to run a sync from the Airbyte UI

Once we've completed the above steps, we will have built a functioning connector. Then, we'll add some optional functionality:

* Support [incremental sync](../architecture/incremental.md)
* Add custom integration tests

### 1. Bootstrap the connector package

We'll start the process from the Airbyte repository root:

```bash
$ pwd
/Users/sherifnada/code/airbyte
```

First, let's create a new branch:

```bash
$ git checkout -b $(whoami)/source-connector-tutorial
Switched to a new branch 'sherifnada/source-connector-tutorial'
```

Airbyte provides a code generator which bootstraps the scaffolding for our connector. Let's use it by running:

```bash
$ cd airbyte-integrations/connector-templates/generator
# Install NPM from https://www.npmjs.com/get-npm if you don't have it
$ npm install
$ npm run generate
```

We'll select the `generic` template and call the connector `stock-ticker-api`:

![](../.gitbook/assets/newsourcetutorial_plop.gif)

Note: The generic template is very bare. If you are planning on developing a python source, we recommend using the `python` template. It provides some convenience code to help reduce boilerplate. This tutorial uses the bare-bones version because it makes it easier to see how all the pieces of a connector work together. You can find a walk through on how to build a python connector here \(**coming soon**\).

Head to the connector directory and we should see the following files have been generated:

```bash
$ cd ../../connectors/source-stock-ticker-api
$ ls
Dockerfile              NEW_SOURCE_CHECKLIST.md              build.gradle
```

We'll use each of these files later. But first, let's write some code!

### 2. Implement the connector in line with the Airbyte Specification

In the connector package directory, create a single python file `source.py` that will hold our implementation:

```bash
touch source.py
```

#### Implement the spec operation

At this stage in the tutorial, we just want to implement the `spec` operation as described in the [Airbyte Protocol](https://docs.airbyte.io/architecture/airbyte-specification#spec). This involves a couple of steps:

1. Decide which inputs we need from the user in order to connect to the stock ticker API i.e: the connector's specification, and encode it as a JSON file.
2. Identify when the connector has been invoked with the `spec` operation and return the specification as an `AirbyteMessage`

To contact the stock ticker API, we need two things:

1. Which stock ticker we're interested in
2. The API key to use when contacting the API \(you can obtain a free API token from the [IEX Cloud](https://iexcloud.io/) free plan\)

For reference, the API docs we'll be using [can be found here](https://iexcloud.io/docs/api/).

Let's create a [JSONSchema](http://json-schema.org/) file `spec.json` encoding these two requirements:

```javascript
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
        "title": "API Key",
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
* `airbyte_secret` used by Airbyte to determine if the field should be displayed as a password \(e.g: `********`\) in the UI and not readable from the API.

We'll save this file in the root directory of our connector. Now we have the following files:

```bash
$ ls -1
Dockerfile
NEW_SOURCE_CHECKLIST.md
build.gradle
source.py
spec.json
```

Now, let's edit `source.py` to detect if the program was invoked with the `spec` argument and if so, output the connector specification.

```python
# source.py
import argparse  # helps parse commandline arguments
import json
import sys
import os


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def log(message):
    log_json = {"type": "LOG", "log": message}
    print(json.dumps(log_json))


def spec():
    # Read the file named spec.json from the module directory as a JSON file
    current_script_directory = os.path.dirname(os.path.realpath(__file__))
    spec_path = os.path.join(current_script_directory, "spec.json")
    specification = read_json(spec_path)

    # form an Airbyte Message containing the spec and print it to stdout
    airbyte_message = {"type": "SPEC", "spec": specification}
    # json.dumps converts the JSON (python dict) to a string
    print(json.dumps(airbyte_message))


def run(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title="commands", dest="command")

    # Accept the spec command
    subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()
    else:
        # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log("Invalid command. Allowable commands: [spec]")
        sys.exit(1)

    # A zero exit code means the process successfully completed    
    sys.exit(0)


def main():
    arguments = sys.argv[1:]
    run(arguments)


if __name__ == "__main__":
    main()
```

Some notes on the above code:

1. As described in the [specification](https://docs.airbyte.io/architecture/airbyte-specification#key-takeaways), Airbyte connectors are CLIs which communicate via stdout, so the output of the command is simply a JSON string formatted according to the Airbyte Specification. So to "return" a value we use `print` to output the return value to stdout.
2. All Airbyte commands can output log messages that take the form `{"type":"LOG", "log":"message"}`, so we create a helper method `log(message)` to allow logging.

Now if we run `python source.py spec` we should see the specification printed out:

```bash
python source.py spec
{"type": "SPEC", "spec": {"documentationUrl": "https://iexcloud.io/docs/api", "connectionSpecification": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "required": ["stock_ticker", "api_key"], "additionalProperties": false, "properties": {"stock_ticker": {"type": "string", "title": "Stock Ticker", "description": "The stock ticker to track", "examples": ["AAPL", "TSLA", "AMZN"]}, "api_key": {"type": "string", "description": "The IEX Cloud API key to use to hit the API.", "airbyte_secret": true}}}}}
```

We've implemented the first command! Three more and we'll have a working connector.

#### Implementing check connection

The second command to implement is the [check operation](https://docs.airbyte.io/architecture/airbyte-specification#key-takeaways) `check --config <config_name>`, which tells the user whether a config file they gave us is correct. In our case, "correct" means they input a valid stock ticker and a correct API key like we declare via the `spec` operation.

To achieve this, we'll:

1. Create valid and invalid configuration files to test the success and failure cases with our connector. We'll place config files in the `secrets/` directory which is gitignored everywhere in the Airbyte monorepo by default to avoid accidentally checking in API keys.
2. Add a `check` method which calls the IEX Cloud API to verify if the provided token & stock ticker are correct and output the correct airbyte message.
3. Extend the argument parser to recognize the `check --config <config>` command and call the `check` method when the `check` command is invoked.

Let's first add the configuration files:

```bash
$ mkdir secrets
$ echo '{"api_key": "<put_your_key_here>", "stock_ticker": "TSLA"}' > secrets/valid_config.json
$ echo '{"api_key": "not_a_real_key", "stock_ticker": "TSLA"}' > secrets/invalid_config.json
```

Make sure to add your actual API key \(the private key\) instead of the placeholder value `<put_your_key_here>` when following the tutorial.

Then we'll add the `check_method`:

```python
def _call_api(endpoint, token):
    return requests.get("https://cloud.iexapis.com/v1/" + endpoint + "?token=" + token)


def check(config):
    # Validate input configuration by attempting to get the price of the input stock ticker for the previous day
    response = _call_api(endpoint="stock/" + config["stock_ticker"] + "/previous", token=config["api_key"])
    if response.status_code == 200:
        result = {"status": "SUCCEEDED"}
    elif response.status_code == 403:
        # HTTP code 403 means authorization failed so the API key is incorrect
        result = {"status": "FAILED", "message": "API Key is incorrect."}
    else:
        result = {"status": "FAILED", "message": "Input configuration is incorrect. Please verify the input stock ticker and API key."}

    output_message = {"type": "CONNECTION_STATUS", "connectionStatus": result}
    print(json.dumps(output_message))
```

Lastly we'll extend the `run` method to accept the `check` command and call the `check` method. First we'll add a helper method for reading input:

```python
def get_input_file_path(path):
    if os.path.isabs(path):
        return path
    else: 
        return os.path.join(os.getcwd(), path)
```

In Airbyte, the contract for input files is that they will be available in the current working directory if they are not provided as an absolute path. This method helps us achieve that.

and the following blocks in the argument parser in the run method:

```python
    # Accept the check command
    check_parser = subparsers.add_parser("check", help="checks the config used to connect", parents=[parent_parser])
    required_check_parser = check_parser.add_argument_group("required named arguments")
    required_check_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
```

and

```python
elif command == "check":
    config_file_path = get_input_file_path(parsed_args.config)
    config = read_json(config_file_path)
    check(config)
```

This results in the following `run` method.

```python
def run(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title="commands", dest="command")

    # Accept the spec command
    subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

    # Accept the check command
    check_parser = subparsers.add_parser("check", help="checks the config used to connect", parents=[parent_parser])
    required_check_parser = check_parser.add_argument_group("required named arguments")
    required_check_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()
    elif command == "check":
        config_file_path = get_input_file_path(parsed_args.config)
        config = read_json(config_file_path)
        check(config)
    else:
        # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log("Invalid command. Allowable commands: [spec, check]")
        sys.exit(1)

    # A zero exit code means the process successfully completed
    sys.exit(0)
```

and that should be it. Let's test our new method:

```bash
$ python source.py check --config secrets/valid_config.json
{'type': 'CONNECTION_STATUS', 'connectionStatus': {'status': 'SUCCEEDED'}}
$ python source.py check --config secrets/invalid_config.json
{'type': 'CONNECTION_STATUS', 'connectionStatus': {'status': 'FAILED', 'message': 'API Key is incorrect.'}}
```

Our connector is able to detect valid and invalid configs correctly. Two methods down, two more to go!

#### Implementing Discover

The `discover` command outputs a Catalog, a struct that declares the Streams and Fields \(Airbyte's equivalents of tables and columns\) output by the connector. It also includes metadata around which features a connector supports \(e.g. which sync modes\). In other words it describes what data is available in the source. If you'd like to read a bit more about this concept check out our [Beginner's Guide to the Airbyte Catalog](beginners-guide-to-catalog.md) or for a more detailed treatment read the [Airbyte Specification](../architecture/airbyte-specification.md).

The data output by this connector will be structured in a very simple way. This connector outputs records belonging to exactly one Stream \(table\). Each record contains three Fields \(columns\): `date`, `price`, and `stock_ticker`, corresponding to the price of a stock on a given day.

To implement `discover`, we'll:

1. Add a method `discover` in `source.py` which outputs the Catalog. To better understand what a catalog is, check out our [Beginner's Guide to the AirbyteCatalog](beginners-guide-to-catalog.md).
2. Extend the arguments parser to use detect the `discover --config <config_path>` command and call the `discover` method.

Let's implement `discover` by adding the following in `source.py`:

```python
def discover():
    catalog = {
        "streams": [{
            "name": "stock_prices",
            "supported_sync_modes": ["full_refresh"],
            "json_schema": {
                "properties": {
                    "date": {
                        "type": "string"
                    },
                    "price": {
                        "type": "number"
                    },
                    "stock_ticker": {
                        "type": "string"
                    }
                }
            }
        }]
    }
    airbyte_message = {"type": "CATALOG", "catalog": catalog}
    print(json.dumps(airbyte_message))
```

Note that we describe the schema of the output stream using [JSONSchema](http://json-schema.org/).

Then we'll extend the arguments parser by adding the following blocks to the `run` method:

```python
# Accept the discover command
discover_parser = subparsers.add_parser("discover", help="outputs a catalog describing the source's schema", parents=[parent_parser])
required_discover_parser = discover_parser.add_argument_group("required named arguments")
required_discover_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
```

and

```python
elif command == "discover":
    discover()
```

You may be wondering why `config` is a required input to `discover` if it's not used. This is done for consistency: the Airbyte Specification requires `--config` as an input to `discover` because many sources require it \(e.g: to discover the tables available in a Postgres database, you must supply a password\). So instead of guessing whether the flag is required depending on the connector, we always assume it is required, and the connector can choose whether to use it.

The full run method is now below:

```python
def run(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title="commands", dest="command")

    # Accept the spec command
    subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

    # Accept the check command
    check_parser = subparsers.add_parser("check", help="checks the config used to connect", parents=[parent_parser])
    required_check_parser = check_parser.add_argument_group("required named arguments")
    required_check_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

    # Accept the discover command
    discover_parser = subparsers.add_parser("discover", help="outputs a catalog describing the source's schema", parents=[parent_parser])
    required_discover_parser = discover_parser.add_argument_group("required named arguments")
    required_discover_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()
    elif command == "check":
        config_file_path = get_input_file_path(parsed_args.config)
        config = read_json(config_file_path)
        check(config)
    elif command == "discover":
        discover()
    else:
        # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log("Invalid command. Allowable commands: [spec, check, discover]")
        sys.exit(1)

    # A zero exit code means the process successfully completed
    sys.exit(0)
```

Let's test our new command:

```bash
$ python source.py discover --config secrets/valid_config.json
{"type": "CATALOG", "catalog": {"streams": [{"name": "stock_prices", "supported_sync_modes": ["full_refresh"], "json_schema": {"properties": {"date": {"type": "string"}, "price": {"type": "number"}, "stock_ticker": {"type": "string"}}}}]}}
```

With that, we're done implementing the `discover` command.

#### Implementing the read operation

We've done a lot so far, but a connector ultimately exists to read data! This is where the [`read` command](https://docs.airbyte.io/architecture/airbyte-specification#read) comes in. The format of the command is:

```bash
python source.py read --config <config_file_path> --catalog <configured_catalog.json> [--state <state_file_path>]
```

Each of these are described in the Airbyte Specification in detail, but we'll give a quick description of the two options we haven't seen so far:

* `--catalog` points to a Configured Catalog. The Configured Catalog contains the contents for the Catalog \(remember the Catalog we output from discover?\). It also contains some configuration information that describes how the data will by replicated. For example, we had `supported_sync_modes` in the Catalog. In the Configured Catalog, we select which of the `supported_sync_modes` we want to use by specifying the `sync_mode` field. \(This is the most complicated concept when working Airbyte, so if it is still not making sense that's okay for now. If you're just dying to understand how the Configured Catalog works checkout the [Beginner's Guide to the Airbyte Catalog](beginners-guide-to-catalog.md).\)
* `--state` points to a state file. The state file is only relevant when some Streams are synced with the sync mode `incremental`, so we'll cover the state file in more detail in the incremental section below.

For our connector, the contents of those two files should be very unsurprising: the connector only supports one Stream, `stock_prices`, so we'd expect the input catalog to contain that stream configured to sync in full refresh. Since our connector doesn't support incremental sync \(yet!\) we'll ignore the state option for now.

To read data in our connector, we'll:

1. Create a configured catalog which tells our connector that we want to sync the `stock_prices` stream.
2. Implement a method `read` in `source.py`. For now we'll always read the last 7 days of a stock price's data.
3. Extend the arguments parser to recognize the `read` command and its arguments.

First, let's create a configured catalog `fullrefresh_configured_catalog.json` to use as test input for the read operation:

```javascript
{
  "streams": [
    {
      "stream": {
        "name": "stock_prices",
        "supported_sync_modes": [
          "full_refresh"
        ],
        "json_schema": {
          "properties": {
            "date": {
              "type": "string"
            },
            "price": {
              "type": "number"
            },
            "stock_ticker": {
              "type": "string"
            }
          }
        }
      },
      "sync_mode": "full_refresh"
    }
  ]
}
```

Then we'll define the `read` method in `source.py`:

```python
import datetime


def read(config, catalog):
    # Find the stock_prices stream if it is present in the input catalog
    stock_prices_stream = None
    for configured_stream in catalog["streams"]:
        if configured_stream["stream"]["name"] == "stock_prices":
            stock_prices_stream = configured_stream

    if stock_prices_stream is None:
        log("No streams selected")
        return

    # We only support full_refresh at the moment, so verify the user didn't ask for another sync mode
    if stock_prices_stream["sync_mode"] != "full_refresh":
        log("This connector only supports full refresh syncs! (for now)")
        sys.exit(1)

    # If we've made it this far, all the configuration is good and we can pull the last 7 days of market data
    api_key = config["api_key"]
    stock_ticker = config["stock_ticker"]
    response = _call_api(f"/stock/{stock_ticker}/chart/7d", api_key)
    if response.status_code != 200:
        # In a real scenario we'd handle this error better :)
        log("Failure occurred when calling IEX API")
        sys.exit(1)
    else:
        # Sort the stock prices ascending by date then output them one by one as AirbyteMessages
        prices = sorted(response.json(), key=lambda record: datetime.datetime.strptime(record["date"], '%Y-%m-%d'))
        for price in prices:
            data = {"date": price["date"], "stock_ticker": price["symbol"], "price": price["close"]}
            # emitted_at is in milliseconds so we multiply by 1000
            record = {"stream": "stock_prices", "data": data, "emitted_at": int(datetime.datetime.now().timestamp()) * 1000}
            output_message = {"type": "RECORD", "record": record}
            print(json.dumps(output_message))
```

After doing some input validation, the code above calls the API to obtain the last 7 days of prices for the input stock ticker, then outputs the prices in ascending order. As always, our output is formatted according to the Airbyte Specification. Let's update our args parser with the following blocks:

```python
# Accept the read command
read_parser = subparsers.add_parser("read", help="reads the source and outputs messages to STDOUT", parents=[parent_parser])
read_parser.add_argument("--state", type=str, required=False, help="path to the json-encoded state file")
required_read_parser = read_parser.add_argument_group("required named arguments")
required_read_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
required_read_parser.add_argument(
    "--catalog", type=str, required=True, help="path to the catalog used to determine which data to read"
)
```

and:

```python
elif command == "read":
    config = read_json(get_input_file_path(parsed_args.config))
    configured_catalog = read_json(get_input_file_path(parsed_args.catalog))
    read(config, configured_catalog)
```

this yields the following `run` method:

```python
def run(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title="commands", dest="command")

    # Accept the spec command
    subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

    # Accept the check command
    check_parser = subparsers.add_parser("check", help="checks the config used to connect", parents=[parent_parser])
    required_check_parser = check_parser.add_argument_group("required named arguments")
    required_check_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

    # Accept the discover command
    discover_parser = subparsers.add_parser("discover", help="outputs a catalog describing the source's schema", parents=[parent_parser])
    required_discover_parser = discover_parser.add_argument_group("required named arguments")
    required_discover_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

    # Accept the read command
    read_parser = subparsers.add_parser("read", help="reads the source and outputs messages to STDOUT", parents=[parent_parser])
    read_parser.add_argument("--state", type=str, required=False, help="path to the json-encoded state file")
    required_read_parser = read_parser.add_argument_group("required named arguments")
    required_read_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
    required_read_parser.add_argument(
        "--catalog", type=str, required=True, help="path to the catalog used to determine which data to read"
    )

    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()
    elif command == "check":
        config_file_path = get_input_file_path(parsed_args.config)
        config = read_json(config_file_path)
        check(config)
    elif command == "discover":
        discover()
    elif command == "read":
        config = read_json(get_input_file_path(parsed_args.config))
        configured_catalog = read_json(get_input_file_path(parsed_args.catalog))
        read(config, configured_catalog)
    else:
        # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log("Invalid command. Allowable commands: [spec, check, discover, read]")
        sys.exit(1)

    # A zero exit code means the process successfully completed
    sys.exit(0)
```

Let's test out our new command:

```bash
$ python source.py read --config secrets/valid_config.json --catalog fullrefresh_configured_catalog.json
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-15', 'stock_ticker': 'TSLA', 'price': 633.25}, 'emitted_at': 1608626365000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-16', 'stock_ticker': 'TSLA', 'price': 622.77}, 'emitted_at': 1608626365000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-17', 'stock_ticker': 'TSLA', 'price': 655.9}, 'emitted_at': 1608626365000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-18', 'stock_ticker': 'TSLA', 'price': 695}, 'emitted_at': 1608626365000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-21', 'stock_ticker': 'TSLA', 'price': 649.86}, 'emitted_at': 1608626365000}}
```

With this method, we now have a fully functioning connector! Let's pat ourselves on the back for getting there.

For reference, the full `source.py` file now looks like this:

```python
# source.py
import argparse  # helps parse commandline arguments
import json
import sys
import os
import requests
import datetime


def read(config, catalog):
    # Find the stock_prices stream if it is present in the input catalog
    stock_prices_stream = None
    for configured_stream in catalog["streams"]:
        if configured_stream["stream"]["name"] == "stock_prices":
            stock_prices_stream = configured_stream

    if stock_prices_stream is None:
        log("No streams selected")
        return

    # We only support full_refresh at the moment, so verify the user didn't ask for another sync mode
    if stock_prices_stream["sync_mode"] != "full_refresh":
        log("This connector only supports full refresh syncs! (for now)")
        sys.exit(1)

    # If we've made it this far, all the configuration is good and we can pull the last 7 days of market data
    api_key = config["api_key"]
    stock_ticker = config["stock_ticker"]
    response = _call_api(f"/stock/{stock_ticker}/chart/7d", api_key)
    if response.status_code != 200:
        # In a real scenario we'd handle this error better :)
        log("Failure occurred when calling IEX API")
        sys.exit(1)
    else:
        # Sort the stock prices ascending by date then output them one by one as AirbyteMessages
        prices = sorted(response.json(), key=lambda record: datetime.datetime.strptime(record["date"], '%Y-%m-%d'))
        for price in prices:
            data = {"date": price["date"], "stock_ticker": price["symbol"], "price": price["close"]}
            record = {"stream": "stock_prices", "data": data, "emitted_at": int(datetime.datetime.now().timestamp()) * 1000}
            output_message = {"type": "RECORD", "record": record}
            print(json.dumps(output_message))


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def _call_api(endpoint, token):
    return requests.get("https://cloud.iexapis.com/v1/" + endpoint + "?token=" + token)


def check(config):
    # Validate input configuration by attempting to get the price of the input stock ticker for the previous day
    response = _call_api(endpoint="stock/" + config["stock_ticker"] + "/previous", token=config["api_key"])
    if response.status_code == 200:
        result = {"status": "SUCCEEDED"}
    elif response.status_code == 403:
        # HTTP code 403 means authorization failed so the API key is incorrect
        result = {"status": "FAILED", "message": "API Key is incorrect."}
    else:
        # Consider any other code a "generic" failure and tell the user to make sure their config is correct.
        result = {"status": "FAILED", "message": "Input configuration is incorrect. Please verify the input stock ticker and API key."}

    # Format the result of the check operation according to the Airbyte Specification
    output_message = {"type": "CONNECTION_STATUS", "connectionStatus": result}
    print(json.dumps(output_message))


def log(message):
    log_json = {"type": "LOG", "log": message}
    print(json.dumps(log_json))


def discover():
    catalog = {
        "streams": [{
            "name": "stock_prices",
            "supported_sync_modes": ["full_refresh"],
            "json_schema": {
                "properties": {
                    "date": {
                        "type": "string"
                    },
                    "price": {
                        "type": "number"
                    },
                    "stock_ticker": {
                        "type": "string"
                    }
                }
            }
        }]
    }
    airbyte_message = {"type": "CATALOG", "catalog": catalog}
    print(json.dumps(airbyte_message))


def get_input_file_path(path):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(os.getcwd(), path)


def spec():
    # Read the file named spec.json from the module directory as a JSON file
    current_script_directory = os.path.dirname(os.path.realpath(__file__))
    spec_path = os.path.join(current_script_directory, "spec.json")
    specification = read_json(spec_path)

    # form an Airbyte Message containing the spec and print it to stdout
    airbyte_message = {"type": "SPEC", "spec": specification}
    # json.dumps converts the JSON (python dict) to a string
    print(json.dumps(airbyte_message))


def run(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title="commands", dest="command")

    # Accept the spec command
    subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

    # Accept the check command
    check_parser = subparsers.add_parser("check", help="checks the config used to connect", parents=[parent_parser])
    required_check_parser = check_parser.add_argument_group("required named arguments")
    required_check_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

    # Accept the discover command
    discover_parser = subparsers.add_parser("discover", help="outputs a catalog describing the source's schema", parents=[parent_parser])
    required_discover_parser = discover_parser.add_argument_group("required named arguments")
    required_discover_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")

    # Accept the read command
    read_parser = subparsers.add_parser("read", help="reads the source and outputs messages to STDOUT", parents=[parent_parser])
    read_parser.add_argument("--state", type=str, required=False, help="path to the json-encoded state file")
    required_read_parser = read_parser.add_argument_group("required named arguments")
    required_read_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
    required_read_parser.add_argument(
        "--catalog", type=str, required=True, help="path to the catalog used to determine which data to read"
    )

    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()
    elif command == "check":
        config_file_path = get_input_file_path(parsed_args.config)
        config = read_json(config_file_path)
        check(config)
    elif command == "discover":
        discover()
    elif command == "read":
        config = read_json(get_input_file_path(parsed_args.config))
        configured_catalog = read_json(get_input_file_path(parsed_args.catalog))
        read(config, configured_catalog)
    else:
        # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log("Invalid command. Allowable commands: [spec, check, discover, read]")
        sys.exit(1)

    # A zero exit code means the process successfully completed
    sys.exit(0)


def main():
    arguments = sys.argv[1:]
    run(arguments)


if __name__ == "__main__":
    main()
```

A full connector in less than 200 lines of code. Not bad! We're now ready to package & test our connector then use it in the Airbyte UI.

### 3. Package the connector in a Docker image

Our connector is very lightweight, so the Dockerfile needed to run it is very light as well. We edit the autogenerated `Dockerfile` so that its contents are as followed:

```text
FROM python:3.7-slim

# We change to a directory unique to us
WORKDIR /airbyte/integration_code
# Install any needed python dependencies
RUN pip install requests
# Copy source files
COPY source.py .
COPY spec.json .

# When this container is invoked, append the input argemnts to `python source.py`
ENTRYPOINT ["python", "/airbyte/integration_code/source.py"]

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.name=airbyte/source-stock-ticker-api
LABEL io.airbyte.version=0.1.0
```

Once we save the `Dockerfile`, we can build the image by running:

```bash
docker build . -t airbyte/source-stock-ticker-api:dev
```

Then we can run the image using:

```bash
docker run airbyte/source-stock-ticker-api:dev
```

to run any of our commands, we'll need to mount all the inputs into the Docker container first, then refer to their _mounted_ paths when invoking the connector. For example, we'd run `check` or `read` as follows:

```bash
$ docker run airbyte/source-stock-ticker-api:dev spec
{"type": "SPEC", "spec": {"documentationUrl": "https://iexcloud.io/docs/api", "connectionSpecification": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "required": ["stock_ticker", "api_key"], "additionalProperties": false, "properties": {"stock_ticker": {"type": "string", "title": "Stock Ticker", "description": "The stock ticker to track", "examples": ["AAPL", "TSLA", "AMZN"]}, "api_key": {"type": "string", "description": "The IEX Cloud API key to use to hit the API.", "airbyte_secret": true}}}}}

$ docker run -v $(pwd)/secrets/valid_config.json:/data/config.json airbyte/source-stock-ticker-api:dev check --config /data/config.json
{'type': 'CONNECTION_STATUS', 'connectionStatus': {'status': 'SUCCEEDED'}}

$ docker run -v $(pwd)/secrets/valid_config.json:/data/config.json airbyte/source-stock-ticker-api:dev discover --config /data/config.json
{"type": "CATALOG", "catalog": {"streams": [{"name": "stock_prices", "supported_sync_modes": ["full_refresh"], "json_schema": {"properties": {"date": {"type": "string"}, "price": {"type": "number"}, "stock_ticker": {"type": "string"}}}}]}}

$ docker run -v $(pwd)/secrets/valid_config.json:/data/config.json -v $(pwd)/fullrefresh_configured_catalog.json:/data/fullrefresh_configured_catalog.json airbyte/source-stock-ticker-api:dev read --config /data/config.json --catalog /data/fullrefresh_configured_catalog.json
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-15', 'stock_ticker': 'TSLA', 'price': 633.25}, 'emitted_at': 1608628424000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-16', 'stock_ticker': 'TSLA', 'price': 622.77}, 'emitted_at': 1608628424000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-17', 'stock_ticker': 'TSLA', 'price': 655.9}, 'emitted_at': 1608628424000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-18', 'stock_ticker': 'TSLA', 'price': 695}, 'emitted_at': 1608628424000}}
{'type': 'RECORD', 'record': {'stream': 'stock_prices', 'data': {'date': '2020-12-21', 'stock_ticker': 'TSLA', 'price': 649.86}, 'emitted_at': 1608628424000}}
```

and with that, we've packaged our connector in a functioning Docker image. The last requirement before calling this connector finished is to pass the [Airbyte Standard Test suite](../contributing-to-airbyte/building-new-connector/testing-connectors.md).

### 4. Test the connector

The minimum requirement for testing our connector is to pass the Airbyte Standard Test suite. You're encouraged to add custom test cases for your connector where it makes sense to do so e.g: to test edge cases that are not covered by the standard suite. But at the very least, you must pass Airbyte's Standard Test suite.

To integrate with the standard test suite, modify the generated `build.gradle` file as follows:

```groovy
plugins {
    // Makes building the docker image a dependency of Gradle's "build" command. This way you could run your entire build inside a docker image
    // via ./gradlew :airbyte-integrations:connectors:source-stock-ticker-api:build
    id 'airbyte-docker'
    id 'airbyte-standard-source-test-file'
}

airbyteStandardSourceTestFile {
    // All these input paths must live inside this connector's directory (or subdirectories)
    configPath = "secrets/valid_config.json"
    configuredCatalogPath = "fullrefresh_configured_catalog.json"
    specPath = "spec.json"
}

dependencies {
    implementation files(project(':airbyte-integrations:bases:base-standard-source-test-file').airbyteDocker.outputs)
}
```

Then **from the Airbyte repository root**, run:

```bash
./gradlew clean :airbyte-integrations:connectors:source-stock-ticker-api:integrationTest
```

After tests have run, you should see a test summary like:

```text
Test run finished after 5049 ms
[         2 containers found      ]
[         0 containers skipped    ]
[         2 containers started    ]
[         0 containers aborted    ]
[         2 containers successful ]
[         0 containers failed     ]
[         7 tests found           ]
[         0 tests skipped         ]
[         7 tests started         ]
[         0 tests aborted         ]
[         7 tests successful      ]
[         0 tests failed          ]
```

That's it! We've created a fully functioning connector. Now let's get to the exciting part: using it from the Airbyte UI.

### Use the connector in the Airbyte UI

Let's recap what we've achieved so far:

1. Implemented a connector
2. Packaged it in a Docker image
3. Integrated it with the Airbyte Standard Test suite

To use it from the Airbyte UI, we need to:

1. Publish our connector's Docker image somewhere accessible by Airbyte Core \(Airbyte's server, scheduler, workers, and webapp infrastructure\).
2. Add the connector via the Airbyte UI and setup a connection from our new connector to a local CSV file for illustration purposes.
3. Run a sync and inspect the output.

#### 1. Publish the Docker image

Since we're running this tutorial locally, Airbyte will have access to any Docker images available to your local `docker` daemon. So all we need to do is build & tag our connector. If you want your connector to be available to everyone using Airbyte, you'll need to publish it to `Dockerhub`. [Open a PR](https://github.com/airbytehq/airbyte) or visit our [Slack](https://slack.airbyte.io) for help with this.

Airbyte's build system builds and tags your connector's image correctly by default as part of the connector's standard `build` process. **From the Airbyte repo root**, run:

```bash
./gradlew clean :airbyte-integrations:connectors:source-stock-ticker-api:build
```

This is the equivalent of running `docker build . -t airbyte/source-stock-ticker-api:dev` from the connector root, where the tag `airbyte/source-stock-ticker-api` is extracted from the label `LABEL io.airbyte.name` inside your `Dockerfile`.

Verify the image was built by running:

```bash
$  docker images | head
  REPOSITORY                                                    TAG                 IMAGE ID       CREATED          SIZE
  airbyte/source-stock-ticker-api                               dev                 9494ea93b7d0   16 seconds ago   121MB
  <none>                                                        <none>              8fe5b49f9ae5   3 hours ago      121MB
  <none>                                                        <none>              4cb00a551b3c   3 hours ago      121MB
  <none>                                                        <none>              1caf57c72afd   3 hours ago      121MB
```

`airbyte/source-stock-ticker-api` was built and tagged with the `dev` tag. Now let's head to the last step.

#### 2. Add the connector via the Airbyte UI

If the Airbyte server isn't already running, start it by running **from the Airbyte repository root**:

```bash
docker-compose up
```

Then visiting [locahost:8000](http://localhost:8000) in your browser once Airbyte has started up \(it can take 10-20 seconds for the server to start\).

If this is the first time using the Airbyte UI, then you will be prompted to go through a first-time wizard. We will make this something you can skip in the future. For now, we suggest just running through it quickly. If you use the exchange rates api as a source and json as your destination, it should be relatively easy to set up.

In the UI, click the "Admin" button in the left side bar:

![](../.gitbook/assets/newsourcetutorial_sidebar_admin.png)

Then on the admin page, click "New Connector":

![](../.gitbook/assets/newsourcetutorial_admin_page.png)

On the modal that pops up, enter the following information then click "Add"

![](../.gitbook/assets/newsourcetutorial_new_connector_modal.png)

Now from the "Sources" page \(if not redirected, click "Sources" on the left panel\) , click the "New source" button. You'll be taken to the detail page for adding a new source. Choose the "Stock Ticker API" source and add the following information, then click "Set up source":

![](../.gitbook/assets/newsourcetutorial_source_config.png)

on the following page, click the "add destination" button then "add new destination":

![](../.gitbook/assets/newsourcetutorial_add_destination.png)

Configure a local JSON destination as follows: Note that we setup the output directory to `/local/tutorial_json`. When we run syncs, we'll find the output on our local filesystem in `/tmp/airbyte_local/tutorial_json`.

![](../.gitbook/assets/newsourcetutorial_destination_config.png)

Finally, setup the connection configuration:

![](../.gitbook/assets/newsourcetutorial_schema_select.png)

We'll choose the "manual" frequency, meaning we need to launch each sync by hand.

We've setup our connection! Now let's move data.

#### 3. Run a sync from the UI

To launch the sync, click the "sync now" button:

![](../.gitbook/assets/newsourcetutorial_launchsync.png)

If you click on the connector row, you should be taken to the sync detail page. After a few seconds \(refresh the page if the status doesn't change to "succeeded" in a few seconds\), the status of the sync should change to `succeeded` as below:

![](../.gitbook/assets/newsourcetutorial_syncdetail.png)

Let's verify the output. From your shell, run:

```bash
$ airbyte_local cat /tmp/airbyte_local/tutorial_json/stock_prices_raw.jsonl
  {"ab_id":"5fd36107-6a79-4d64-ab36-900184b3848c","emitted_at":1608877192000,"data":{"date":"2020-12-18","stock_ticker":"TSLA","price":695}}
  {"ab_id":"8109396a-e3b9-4ada-b527-2f539c9e016e","emitted_at":1608877192000,"data":{"date":"2020-12-21","stock_ticker":"TSLA","price":649.86}}
  {"ab_id":"203f5d55-260a-44c7-9b70-d4fb79b55aa5","emitted_at":1608877192000,"data":{"date":"2020-12-22","stock_ticker":"TSLA","price":640.34}}
  {"ab_id":"4ee525c6-ee96-4b0c-889d-555ee23298e0","emitted_at":1608877192000,"data":{"date":"2020-12-23","stock_ticker":"TSLA","price":645.98}}
  {"ab_id":"240157c9-b226-438e-8ffd-5039c91ff882","emitted_at":1608877192000,"data":{"date":"2020-12-24","stock_ticker":"TSLA","price":661.77}}
```

Congratulations! We've successfully written a fully functioning Airbyte connector. You're an Airbyte contributor now ;\)

Armed with the knowledge you gained in this guide, here are some places you can go from here:

1. Implement Incremental Sync for your connector \(described in the sections below\)
2. Implement another connector using the language specific helpers listed below
3. While not required, we love contributions! if you end up creating a new connector, we're here to help you make it available to everyone using Airbyte. Remember that you're never expected to maintain a connector by yourself if you merge it to Airbyte -- we're committed to supporting connectors if you can't do it yourself.

## Optional additions

This section is not yet complete and will be completed soon. Please reach out to us on [Slack](https://slack.airbyte.io) or [Github](https://github.com/airbytehq/airbyte) if you need the information promised by these sections immediately.

### Incremental sync

### Contributing the connector

### Language specific helpers

#### Python

