# source.py

import argparse
import json
import sys
import os
import requests
import datetime

import snowflake.connector

# 1. python3 source.py spec
# 2. python3 source.py check --config secrets/config.json
# 3. python3 source.py discover --config secrets/config.json
# 4. python3 source.py read --config secrets/config.json --catalog test_catalog.json
# Java 14 install 
#       wget --no-check-certificate -c --header  "Cookie: oraclelicense=accept-securebackup-cookie" "https://download.oracle.com/otn/java/jdk/14.0.2+12/205943a0976c4ed48cb16f1043c5c647/jdk-14.0.2_linux-x64_bin.deb"
#       sudo apt install ./jdk-14.0.2_linux-x64_bin.deb

def SnowflakeConnect(config):
    conn = snowflake.connector.connect(user=config["username"],
                                       password=config["password"],
                                       account=config["account"])
    cursor = conn.cursor()

    warehouse = config["warehouse"]
    database = config["database"]
    schema = config["schema"]

    cursor.execute(f"USE WAREHOUSE {warehouse}")
    cursor.execute(f"USE DATABASE {database}")
    cursor.execute(f"USE SCHEMA {schema}")

    return cursor


def dtype_to_json_type(dtype) -> str:
    """Convert Pandas Dataframe types to Airbyte Types.
    :param dtype: Pandas Dataframe type
    :return: Corresponding Airbyte Type
    """
    if dtype == object:
        return "string"
    elif dtype in ("int64", "float64"):
        return "number"
    elif dtype == "bool":
        return "boolean"
    return "string"


def read(config, catalog):
    # Find the table if it is present in the database. 
    snowflake_stream = None
    table = config["table"]
    for configured_stream in catalog["streams"]:
        if configured_stream["stream"]["name"] == f"{table}":
            snowflake_stream = configured_stream

    if snowflake_stream is None:
        log("No streams selected")
        return

    # We only support full_refresh at the moment, so verify the user didn't ask for another sync mode
    if snowflake_stream["sync_mode"] != "full_refresh":
        log("This connector only supports full refresh syncs! (for now)")
        sys.exit(1)

    # Output each row of the table at a time to AirbyteMessages
    cursor = SnowflakeConnect(config)
    try:
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetch_pandas_all()
        for i in range(0, len(data)):
            # Output each row as JSON
            row_json = data.iloc[i].to_json()
            output_message = {"type": "RECORD", "record": {"stream": f"{table}", "data": row_json } }
            print(output_message)

    except Exception as e:
        log(f"FAILED to fetch table. \n\n ERROR MESSAGE: {e}")
        sys.exit(1)


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def check(config):
    # Validate the input configuration with the database
    table = config["table"]
    try:
        cursor = SnowflakeConnect(config)
        cursor.execute(f"SELECT TOP 1 * FROM {table}")
        # Format the result of the check operation according to the Airbyte Specification
        output_message = {"type": "CONNECTION_STATUS", "connectionStatus": "SUCCESS"}
        print(json.dumps(output_message))
    except Exception as e:
        output_message = {"status": "FAILED", "message": "Input configuration is incorrect. Please verify the input in config.json."}
        print(json.dumps(output_message))


def log(message):
    log_json = {"type": "LOG", "log": message}
    print(json.dumps(log_json))


def discover(config):
    # Collect a dataframe and build out a dynamic json schema for this.

    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {}
    }

    # data = 1 row of a dataframe with dtypes and column names to build json
    cursor = SnowflakeConnect(config)
    table = config["table"]
    try:
        cursor.execute(f"SELECT TOP 1 * FROM {table}")
        data = cursor.fetch_pandas_all()

        for i in range(0, len(list(data.columns))):
            attr = list(data.columns)[i]
            d_type = list(data.dtypes)[i]
            d_type = dtype_to_json_type(d_type)
            json_schema["properties"].update({f"{attr}": {"type": f"{d_type}"}})

    except Exception as e:
        print("FAILED", e)

    catalog = {"streams": [{
                    "name": f"{table}",
                    "supported_sync_modes": ["full_refresh"],
                    "json_schema": json_schema

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
        config_file_path = get_input_file_path(parsed_args.config)
        config = read_json(config_file_path)
        discover(config)
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