# source.py
import argparse  # helps parse commandline arguments
import json
import sys
import requests


def read_json(filename):
    with open(filename, "r") as f:
        return json.loads(f.read())


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
            # Consider any other code a "generic" failure and tell the user to make sure their config is correct.
            result = {"status": "FAILED", "message": "Input configuration is incorrect. Please verify the input stock ticker and API key."}

        # Format the result of the check operation according to the Airbyte Specification
        output_message = {"type": "connectionStatus", "connectionStatus": result}
        print(output_message)


def log(message):
    log_json = {"type": "LOG", "log": message}
    print(json.dumps(log_json))


def spec():
    # Read the file named spec.json from the module directory as a JSON file
    specification = read_json("spec.json")

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

    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()
    elif command == "check":
        config_file_path = parsed_args.config
        config = read_json(config_file_path)
        check(config)
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
