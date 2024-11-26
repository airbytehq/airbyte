import asyncio
import json
import logging
import signal as signal_module
import sys
import textwrap
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from typing import Any, Dict, Optional

from graphql import GraphQLError, print_schema
from yarl import URL

from gql import Client, __version__, gql
from gql.transport import AsyncTransport
from gql.transport.exceptions import TransportQueryError

description = """
Send GraphQL queries from the command line using http(s) or websockets.
If used interactively, write your query, then use Ctrl-D (EOF) to execute it.
"""

examples = """
EXAMPLES
========

# Simple query using https
echo 'query { continent(code:"AF") { name } }' | \
gql-cli https://countries.trevorblades.com

# Simple query using websockets
echo 'query { continent(code:"AF") { name } }' | \
gql-cli wss://countries.trevorblades.com/graphql

# Query with variable
echo 'query getContinent($code:ID!) { continent(code:$code) { name } }' | \
gql-cli https://countries.trevorblades.com --variables code:AF

# Interactive usage (insert your query in the terminal, then press Ctrl-D to execute it)
gql-cli wss://countries.trevorblades.com/graphql --variables code:AF

# Execute query saved in a file
cat query.gql | gql-cli wss://countries.trevorblades.com/graphql

# Print the schema of the backend
gql-cli https://countries.trevorblades.com/graphql --print-schema

"""


def positive_int_or_none(value_str: str) -> Optional[int]:
    """Convert a string argument value into either an int or None.

    Raise a ValueError if the argument is negative or a string which is not "none"
    """
    try:
        value_int = int(value_str)
    except ValueError:
        if value_str.lower() == "none":
            return None
        else:
            raise

    if value_int < 0:
        raise ValueError

    return value_int


def get_parser(with_examples: bool = False) -> ArgumentParser:
    """Provides an ArgumentParser for the gql-cli script.

    This function is also used by sphinx to generate the script documentation.

    :param with_examples: set to False by default so that the examples are not
                          present in the sphinx docs (they are put there with
                          a different layout)
    """

    parser = ArgumentParser(
        description=description,
        epilog=examples if with_examples else None,
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "server", help="the server url starting with http://, https://, ws:// or wss://"
    )
    parser.add_argument(
        "-V",
        "--variables",
        nargs="*",
        help="query variables in the form key:json_value",
    )
    parser.add_argument(
        "-H", "--headers", nargs="*", help="http headers in the form key:value"
    )
    parser.add_argument("--version", action="version", version=f"v{__version__}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--debug",
        help="print lots of debugging statements (loglevel==DEBUG)",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    group.add_argument(
        "-v",
        "--verbose",
        help="show low level messages (loglevel==INFO)",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    parser.add_argument(
        "-o",
        "--operation-name",
        help="set the operation_name value",
        dest="operation_name",
    )
    parser.add_argument(
        "--print-schema",
        help="get the schema from instrospection and print it",
        action="store_true",
        dest="print_schema",
    )
    parser.add_argument(
        "--schema-download",
        nargs="*",
        help=textwrap.dedent(
            """select the introspection query arguments to download the schema.
            Only useful if --print-schema is used.
            By default, it will:

             - request field descriptions
             - not request deprecated input fields

            Possible options:

             - descriptions:false             for a compact schema without comments
             - input_value_deprecation:true   to download deprecated input fields
             - specified_by_url:true
             - schema_description:true
             - directive_is_repeatable:true"""
        ),
        dest="schema_download",
    )
    parser.add_argument(
        "--execute-timeout",
        help="set the execute_timeout argument of the Client (default: 10)",
        type=positive_int_or_none,
        default=10,
        dest="execute_timeout",
    )
    parser.add_argument(
        "--transport",
        default="auto",
        choices=[
            "auto",
            "aiohttp",
            "phoenix",
            "websockets",
            "appsync_http",
            "appsync_websockets",
        ],
        help=(
            "select the transport. 'auto' by default: "
            "aiohttp or websockets depending on url scheme"
        ),
        dest="transport",
    )

    appsync_description = """
By default, for an AppSync backend, the IAM authentication is chosen.

If you want API key or JWT authentication, you can provide one of the
following arguments:"""

    appsync_group = parser.add_argument_group(
        "AWS AppSync options", description=appsync_description
    )

    appsync_auth_group = appsync_group.add_mutually_exclusive_group()

    appsync_auth_group.add_argument(
        "--api-key",
        help="Provide an API key for authentication",
        dest="api_key",
    )

    appsync_auth_group.add_argument(
        "--jwt",
        help="Provide an JSON Web token for authentication",
        dest="jwt",
    )

    return parser


def get_transport_args(args: Namespace) -> Dict[str, Any]:
    """Extract extra arguments necessary for the transport
    from the parsed command line args

    Will create a headers dict by splitting the colon
    in the --headers arguments

    :param args: parsed command line arguments
    """

    transport_args: Dict[str, Any] = {}

    # Parse the headers argument
    headers = {}
    if args.headers is not None:
        for header in args.headers:

            try:
                # Split only the first colon (throw a ValueError if no colon is present)
                header_key, header_value = header.split(":", 1)

                headers[header_key] = header_value

            except ValueError:
                raise ValueError(f"Invalid header: {header}")

    if args.headers is not None:
        transport_args["headers"] = headers

    return transport_args


def get_execute_args(args: Namespace) -> Dict[str, Any]:
    """Extract extra arguments necessary for the execute or subscribe
    methods from the parsed command line args

    Extract the operation_name

    Extract the variable_values from the --variables argument
    by splitting the first colon, then loads the json value,
    We try to add double quotes around the value if it does not work first
    in order to simplify the passing of simple string values
    (we allow --variables KEY:VALUE instead of KEY:\"VALUE\")

    :param args: parsed command line arguments
    """

    execute_args: Dict[str, Any] = {}

    # Parse the operation_name argument
    if args.operation_name is not None:
        execute_args["operation_name"] = args.operation_name

    # Parse the variables argument
    if args.variables is not None:

        variables = {}

        for var in args.variables:

            try:
                # Split only the first colon
                # (throw a ValueError if no colon is present)
                variable_key, variable_json_value = var.split(":", 1)

                # Extract the json value,
                # trying with double quotes if it does not work
                try:
                    variable_value = json.loads(variable_json_value)
                except json.JSONDecodeError:
                    try:
                        variable_value = json.loads(f'"{variable_json_value}"')
                    except json.JSONDecodeError:
                        raise ValueError

                # Save the value in the variables dict
                variables[variable_key] = variable_value

            except ValueError:
                raise ValueError(f"Invalid variable: {var}")

        execute_args["variable_values"] = variables

    return execute_args


def autodetect_transport(url: URL) -> str:
    """Detects which transport should be used depending on url."""

    if url.scheme in ["ws", "wss"]:
        transport_name = "websockets"

    else:
        assert url.scheme in ["http", "https"]
        transport_name = "aiohttp"

    return transport_name


def get_transport(args: Namespace) -> Optional[AsyncTransport]:
    """Instantiate a transport from the parsed command line arguments

    :param args: parsed command line arguments
    """

    # Get the url scheme from server parameter
    url = URL(args.server)

    # Validate scheme
    if url.scheme not in ["http", "https", "ws", "wss"]:
        raise ValueError("URL protocol should be one of: http, https, ws, wss")

    # Get extra transport parameters from command line arguments
    # (headers)
    transport_args = get_transport_args(args)

    # Either use the requested transport or autodetect it
    if args.transport == "auto":
        transport_name = autodetect_transport(url)
    else:
        transport_name = args.transport

    # Import the correct transport class depending on the transport name
    if transport_name == "aiohttp":
        from gql.transport.aiohttp import AIOHTTPTransport

        return AIOHTTPTransport(url=args.server, **transport_args)

    elif transport_name == "phoenix":
        from gql.transport.phoenix_channel_websockets import (
            PhoenixChannelWebsocketsTransport,
        )

        return PhoenixChannelWebsocketsTransport(url=args.server, **transport_args)

    elif transport_name == "websockets":
        from gql.transport.websockets import WebsocketsTransport

        transport_args["ssl"] = url.scheme == "wss"

        return WebsocketsTransport(url=args.server, **transport_args)

    else:

        from gql.transport.appsync_auth import AppSyncAuthentication

        assert transport_name in ["appsync_http", "appsync_websockets"]
        assert url.host is not None

        auth: AppSyncAuthentication

        if args.api_key:
            from gql.transport.appsync_auth import AppSyncApiKeyAuthentication

            auth = AppSyncApiKeyAuthentication(host=url.host, api_key=args.api_key)

        elif args.jwt:
            from gql.transport.appsync_auth import AppSyncJWTAuthentication

            auth = AppSyncJWTAuthentication(host=url.host, jwt=args.jwt)

        else:
            from gql.transport.appsync_auth import AppSyncIAMAuthentication
            from botocore.exceptions import NoRegionError

            try:
                auth = AppSyncIAMAuthentication(host=url.host)
            except NoRegionError:
                # A warning message has been printed in the console
                return None

        transport_args["auth"] = auth

        if transport_name == "appsync_http":
            from gql.transport.aiohttp import AIOHTTPTransport

            return AIOHTTPTransport(url=args.server, **transport_args)

        else:
            from gql.transport.appsync_websockets import AppSyncWebsocketsTransport

            try:
                return AppSyncWebsocketsTransport(url=args.server, **transport_args)
            except Exception:
                # This is for the NoCredentialsError but we cannot import it here
                return None


def get_introspection_args(args: Namespace) -> Dict:
    """Get the introspection args depending on the schema_download argument"""

    # Parse the headers argument
    introspection_args = {}

    possible_args = [
        "descriptions",
        "specified_by_url",
        "directive_is_repeatable",
        "schema_description",
        "input_value_deprecation",
    ]

    if args.schema_download is not None:
        for arg in args.schema_download:

            try:
                # Split only the first colon (throw a ValueError if no colon is present)
                arg_key, arg_value = arg.split(":", 1)

                if arg_key not in possible_args:
                    raise ValueError(f"Invalid schema_download: {args.schema_download}")

                arg_value = arg_value.lower()
                if arg_value not in ["true", "false"]:
                    raise ValueError(f"Invalid schema_download: {args.schema_download}")

                introspection_args[arg_key] = arg_value == "true"

            except ValueError:
                raise ValueError(f"Invalid schema_download: {args.schema_download}")

    return introspection_args


async def main(args: Namespace) -> int:
    """Main entrypoint of the gql-cli script

    :param args: The parsed command line arguments
    :return: The script exit code (0 = ok, 1 = error)
    """

    # Set requested log level
    if args.loglevel is not None:
        logging.basicConfig(level=args.loglevel)

    try:
        # Instantiate transport from command line arguments
        transport = get_transport(args)

        if transport is None:
            return 1

        # Get extra execute parameters from command line arguments
        # (variables, operation_name)
        execute_args = get_execute_args(args)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # By default, the exit_code is 0 (everything is ok)
    exit_code = 0

    # Connect to the backend and provide a session
    async with Client(
        transport=transport,
        fetch_schema_from_transport=args.print_schema,
        introspection_args=get_introspection_args(args),
        execute_timeout=args.execute_timeout,
    ) as session:

        if args.print_schema:
            schema_str = print_schema(session.client.schema)
            print(schema_str)

            return exit_code

        while True:

            # Read multiple lines from input and trim whitespaces
            # Will read until EOF character is received (Ctrl-D)
            query_str = sys.stdin.read().strip()

            # Exit if query is empty
            if len(query_str) == 0:
                break

            # Parse query, continue on error
            try:
                query = gql(query_str)
            except GraphQLError as e:
                print(e, file=sys.stderr)
                exit_code = 1
                continue

            # Execute or Subscribe the query depending on transport
            try:
                try:
                    async for result in session.subscribe(query, **execute_args):
                        print(json.dumps(result))
                except KeyboardInterrupt:  # pragma: no cover
                    pass
                except NotImplementedError:
                    result = await session.execute(query, **execute_args)
                    print(json.dumps(result))
            except (GraphQLError, TransportQueryError) as e:
                print(e, file=sys.stderr)
                exit_code = 1

    return exit_code


def gql_cli() -> None:
    """Synchronously invoke ``main`` with the parsed command line arguments.

    Formerly ``scripts/gql-cli``, now registered as an ``entry_point``
    """
    # Get arguments from command line
    parser = get_parser(with_examples=True)
    args = parser.parse_args()

    try:
        # Create a new asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create a gql-cli task with the supplied arguments
        main_task = asyncio.ensure_future(main(args), loop=loop)

        # Add signal handlers to close gql-cli cleanly on Control-C
        for signal_name in ["SIGINT", "SIGTERM", "CTRL_C_EVENT", "CTRL_BREAK_EVENT"]:
            signal = getattr(signal_module, signal_name, None)

            if signal is None:
                continue

            try:
                loop.add_signal_handler(signal, main_task.cancel)
            except NotImplementedError:  # pragma: no cover
                # not all signals supported on all platforms
                pass

        # Run the asyncio loop to execute the task
        exit_code = 0
        try:
            exit_code = loop.run_until_complete(main_task)
        finally:
            loop.close()

        # Return with the correct exit code
        sys.exit(exit_code)
    except KeyboardInterrupt:  # pragma: no cover
        pass
