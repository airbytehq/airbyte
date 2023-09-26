import argparse
import json
from typing import Optional, Union

import requests
import sys
import os

from datetime import date, datetime, timedelta, timezone
from http import HTTPStatus


def _call_api(ticker: str, token: str, from_day: Union[str, date], to_day: Union[str, date]) -> requests.Response:
    return requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_day}/{to_day}?sort=asc&limit=120&apiKey={token}")


def read_json(filepath: str) -> dict:
    with open(filepath, "r") as f:
        return json.loads(f.read())


def get_input_file_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(os.getcwd(), path)


def log(message: str) -> None:
    log_json = {"type": "LOG", "log": message}
    print(json.dumps(log_json))


def log_error(error_message: str) -> None:
    current_time_in_ms = int(datetime.now().timestamp()) * 1000
    log_json = {"type": "TRACE", "trace": {"type": "ERROR", "emitted_at": current_time_in_ms, "error": {"message": error_message}}}
    print(json.dumps(log_json))


def spec() -> None:
    # Read the file named spec.json from the module directory as a JSON file
    current_script_directory = os.path.dirname(os.path.realpath(__file__))
    spec_path = os.path.join(current_script_directory, "spec.json")
    specification = read_json(spec_path)

    # form an Airbyte Message containing the spec and print it to stdout
    airbyte_message = {"type": "SPEC", "spec": specification}
    # json.dumps converts the JSON (Python dict) to a string
    print(json.dumps(airbyte_message))


def check(config: dict) -> None:
    # Validate input configuration by attempting to get the daily closing prices of the input stock ticker
    response = _call_api(
        ticker=config["stock_ticker"],
        token=config["api_key"],
        from_day=datetime.now().date() - timedelta(days=1),
        to_day=datetime.now().date(),
    )
    if response.status_code == HTTPStatus.OK:
        result = {"status": "SUCCEEDED"}
    elif response.status_code == HTTPStatus.FORBIDDEN:
        # HTTP code 403 means authorization failed so the API key is incorrect
        result = {"status": "FAILED", "message": "API Key is incorrect."}
    else:
        result = {"status": "FAILED", "message": "Input configuration is incorrect. Please verify the input stock ticker and API key."}

    output_message = {"type": "CONNECTION_STATUS", "connectionStatus": result}
    print(json.dumps(output_message))


def discover() -> None:
    catalog = {
        "streams": [{
            "name": "stock_prices",
            "supported_sync_modes": ["full_refresh", "incremental"],
            "source_defined_cursor": True,
            "default_cursor_field": ["date"],
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


def read(config: dict, catalog: dict, state: Optional[dict] = None) -> None:
    # Assert required configuration was provided
    if "api_key" not in config or "stock_ticker" not in config:
        log_error("Input config must contain the properties 'api_key' and 'stock_ticker'")
        sys.exit(1)

    # Find the stock_prices stream if it is present in the input catalog
    stock_prices_stream = None
    for configured_stream in catalog["streams"]:
        if configured_stream["stream"]["name"] == "stock_prices":
            stock_prices_stream = configured_stream

    if stock_prices_stream is None:
        log_error("No stream selected.")
        return

    # By default, we fetch stock prices for the 7-day period ending with today
    today = date.today()
    cursor_value = today.strftime("%Y-%m-%d")
    from_day = (today - timedelta(days=7)).strftime("%Y-%m-%d")

    # In case of incremental sync, state should contain the last date when we fetched stock prices
    if stock_prices_stream["sync_mode"] == "incremental":
        if state and "stock_prices" in state and state["stock_prices"].get("date"):
            from_date = datetime.strptime(state["stock_prices"].get("date"), "%Y-%m-%d")
            from_day = (from_date + timedelta(days=1)).strftime("%Y-%m-%d")

    # If the state indicates that we have already run the sync up to cursor_value, we can skip the sync
    if cursor_value > from_day:
        # If we've made it this far, all the configuration is good, and we can pull the market data
        response = _call_api(ticker=config["stock_ticker"], token=config["api_key"], from_day=from_day, to_day=cursor_value)
        if response.status_code != HTTPStatus.OK:
            # In a real scenario we'd handle this error better :)
            log_error("Failure occurred when calling Polygon.io API")
            sys.exit(1)
        else:
            # Stock prices are returned sorted by date in ascending order
            # We want to output them one by one as AirbyteMessages
            response_json = response.json()
            if response_json["resultsCount"] > 0:
                results = response_json["results"]
                for result in results:
                    data = {
                        "date": datetime.fromtimestamp(result["t"]/1000, tz=timezone.utc).strftime("%Y-%m-%d"),
                        "stock_ticker": config["stock_ticker"],
                        "price": result["c"],
                    }
                    record = {"stream": "stock_prices", "data": data, "emitted_at": int(datetime.now().timestamp()) * 1000}
                    output_message = {"type": "RECORD", "record": record}
                    print(json.dumps(output_message))

                    # We update the cursor as we print out the data, so that next time sync starts where we stopped printing out results
                    if stock_prices_stream["sync_mode"] == "incremental":
                        cursor_value = datetime.fromtimestamp(results[len(results)-1]["t"]/1000, tz=timezone.utc).strftime("%Y-%m-%d")

    # Emit new state message.
    if stock_prices_stream["sync_mode"] == "incremental":
        output_message = {"type": "STATE", "state": {"data": {"stock_prices": {"date": cursor_value}}}}
        print(json.dumps(output_message))


def run(args: list) -> None:
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
    discover_parser = subparsers.add_parser(
        "discover", help="outputs a catalog describing the source's schema", parents=[parent_parser]
    )
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
        state = None
        if parsed_args.state:
            state = read_json(get_input_file_path(parsed_args.state))

        read(config, configured_catalog, state)
    else:
        # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log_error("Invalid command. Allowable commands: [spec, check, discover, read]")
        sys.exit(1)

    # A zero exit code means the process successfully completed
    sys.exit(0)


def main() -> None:
    arguments = sys.argv[1:]
    run(arguments)


if __name__ == "__main__":
    main()
