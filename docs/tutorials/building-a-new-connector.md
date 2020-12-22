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

Now, let's edit `source.py` to detect if the program was invoked with the `spec` argument and if so, output the connector specification. 

```python
# source.py
import argparse  # helps parse commandline arguments
import json
import sys


def read_file(filename):
    with open(filename, "r") as f:
        return f.read()


def log(message):
    log_json = {"type": "LOG", "log": message}
    print(json.dumps(log_json))


def spec():
    # Read the file named spec.json from the module directory as a JSON file
    specification = json.loads(read_file("spec.json"))

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
    # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
    # had a failure
    else:
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
1. Airbyte connectors are CLIs which communicate via stdout, so the output of the command is simply a JSON string formatted according to the Airbyte Specification. So to "return" a value we use `print` to output the return value to stdout.  
2. All Airbyte commands can output log messages that take the form `{"type":"LOG", "log":"message"}`, so we create a helper method `log(message)` to allow logging.  

Now if we run `python source.py spec` we should see the specification printed out: 

```
$ python source.py spec
{"type": "SPEC", "spec": {"documentationUrl": "https://iexcloud.io/docs/api", "connectionSpecification": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "required": ["stock_ticker", "api_key"], "additionalProperties": false, "properties": {"stock_ticker": {"type": "string", "title": "Stock Ticker", "description": "The stock ticker to track", "examples": ["AAPL", "TSLA", "AMZN"]}, "api_key": {"type": "string", "description": "The IEX Cloud API key to use to hit the API.", "airbyte_secret": true}}}}}
```

We've implemented the first command! Three more and we'll have a working connector. 

#### Implementing check connection
The second command to implement is `check --config <config_name>`, which tell the user whether a config file they gave us is correct. In our case, "correct" means they input a valid stock ticker and a correct API key like we declare via the `spec` operation. 

To achieve this, we'll: 
1. Create valid and invalid configuration files to test the success and failure cases with our connector. We'll place config files in the `secrets/` directory which is gitignored everywhere in the Airbyte monorepo by default to avoid accidentally checking in API keys. 
2. Add a `check` method which calls the IEX Cloud API to verify if the provided token & stock ticker are correct and output the correct airbyte message 
3. Extend the argument parser to recognize the `check --config <config>` command and call the `check` method when the `check` command is invoked

Let's first add the configuration files: 
```shell script
$ mkdir secrets
$ echo '{"api_key": "<put_your_key_here>", "stock_ticker": "TSLA"}' > secrets/valid_config.json
$ echo '{"api_key": "not_a_real_key", "stock_ticker": "TSLA"}' > secrets/invalid_config1.json
$ echo '{"api_key": "<put_your_key_here>", "stock_ticker": "not_a_real_ticker"}' > secrets/invalid_config2.json
```
Make sure to add your actual API key instead of the placeholder value `<put_your_key_here>` when following the tutorial. 

Then we'll add the `check_method`:
```python
def _call_api(endpoint, token):
    return requests.get("https://cloud.iexapis.com/v1/" + endpoint + "?token=" + token)


def check(config):
    # Assert required configuration was provided
    if "api_key" not in config or "stock_ticker" not in config:
        log("Input config must contain the properties 'api_key' and 'stock_ticker'")
        sys.exit(1)
    else:
        # Validate input configuration by attempting to get the price of the input stock ticker for the previous day
        response = _call_api(endpoint="stock/" + config["stock_ticker"] + "/previous", token=config["api_key"])
        if response.status_code == 200:
            result = {"status": "SUCCEEDED"}
        elif response.status_code == 403:
            # HTTP code 403 means authorization failed so the API key is incorrect
            result = {"status": "FAILED", "message": "API Key is incorrect."}
        else:
            result = {"status": "FAILED", "message": "Input configuration is incorrect. Please verify the input stock ticker and API key."}

        output_message = {"type": "connectionStatus", "connectionStatus": result}
        print(output_message)
```

Lastly we'll extend the `run` method to accept the `check` command and call the `check` method: 
```python
def run(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title="commands", dest="command")

    # Accept the spec command
    subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

    # NEW CODE BEGIN
    # Accept the check command
    check_parser = subparsers.add_parser("check", help="checks the config used to connect", parents=[parent_parser])
    required_check_parser = check_parser.add_argument_group("required named arguments")
    required_check_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
    # NEW CODE END
 
    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()
    # NEW CODE BEGIN
    elif command == "check":
        config_file_path = parsed_args.config
        config = read_json(config_file_path)
        check(config)
    # NEW CODE END
    else:
        # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log("Invalid command. Allowable commands: [spec, discover]")
        sys.exit(1)

    # A zero exit code means the process successfully completed
    sys.exit(0)
```

and that should be it. Let's test our new method method: 

```shell script
$ python source.py check --config secrets/valid_config.json
{'type': 'connectionStatus', 'connectionStatus': {'status': 'SUCCEEDED'}}
$ python source.py check --config secrets/invalid_config1.json
{'type': 'connectionStatus', 'connectionStatus': {'status': 'FAILED', 'message': 'API Key is incorrect.'}}
$ python source.py check --config secrets/invalid_config2.json
{'type': 'connectionStatus', 'connectionStatus': {'status': 'FAILED', 'message': 'Input configuration is incorrect. Please verify the input stock ticker and API key.'}}
```

Our connector is able to detect valid and invalid configs correctly. Two methods down, two more to go!

#### Implementing Discover
The `discover` command declares the Streams and Fields (Airbyte's equivalents of tables and columns) it outputs and the sync modes they support. At a high level 
