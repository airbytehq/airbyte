import json
import logging
from ssl import SSLContext
from typing import Any, Dict, Optional, Tuple, Union, cast
from urllib.parse import urlparse

from graphql import DocumentNode, ExecutionResult, print_ast

from .appsync_auth import AppSyncAuthentication, AppSyncIAMAuthentication
from .exceptions import TransportProtocolError, TransportServerError
from .websockets import WebsocketsTransport, WebsocketsTransportBase

log = logging.getLogger("gql.transport.appsync")

try:
    import botocore
except ImportError:  # pragma: no cover
    # botocore is only needed for the IAM AppSync authentication method
    pass


class AppSyncWebsocketsTransport(WebsocketsTransportBase):
    """:ref:`Async Transport <async_transports>` used to execute GraphQL subscription on
    AWS appsync realtime endpoint.

    This transport uses asyncio and the websockets library in order to send requests
    on a websocket connection.
    """

    auth: Optional[AppSyncAuthentication]

    def __init__(
        self,
        url: str,
        auth: Optional[AppSyncAuthentication] = None,
        session: Optional["botocore.session.Session"] = None,
        ssl: Union[SSLContext, bool] = False,
        connect_timeout: int = 10,
        close_timeout: int = 10,
        ack_timeout: int = 10,
        keep_alive_timeout: Optional[Union[int, float]] = None,
        connect_args: Dict[str, Any] = {},
    ) -> None:
        """Initialize the transport with the given parameters.

        :param url: The GraphQL endpoint URL. Example:
            https://XXXXXXXXXXXXXXXXXXXXXXXXXX.appsync-api.REGION.amazonaws.com/graphql
        :param auth: Optional AWS authentication class which will provide the
                     necessary headers to be correctly authenticated. If this
                     argument is not provided, then we will try to authenticate
                     using IAM.
        :param ssl: ssl_context of the connection.
        :param connect_timeout: Timeout in seconds for the establishment
            of the websocket connection. If None is provided this will wait forever.
        :param close_timeout: Timeout in seconds for the close. If None is provided
            this will wait forever.
        :param ack_timeout: Timeout in seconds to wait for the connection_ack message
            from the server. If None is provided this will wait forever.
        :param keep_alive_timeout: Optional Timeout in seconds to receive
            a sign of liveness from the server.
        :param connect_args: Other parameters forwarded to websockets.connect
        """

        if not auth:

            # Extract host from url
            host = str(urlparse(url).netloc)

            # May raise NoRegionError or NoCredentialsError or ImportError
            auth = AppSyncIAMAuthentication(host=host, session=session)

        self.auth = auth

        url = self.auth.get_auth_url(url)

        super().__init__(
            url,
            ssl=ssl,
            connect_timeout=connect_timeout,
            close_timeout=close_timeout,
            ack_timeout=ack_timeout,
            keep_alive_timeout=keep_alive_timeout,
            connect_args=connect_args,
        )

        # Using the same 'graphql-ws' protocol as the apollo protocol
        self.supported_subprotocols = [
            WebsocketsTransport.APOLLO_SUBPROTOCOL,
        ]
        self.subprotocol = WebsocketsTransport.APOLLO_SUBPROTOCOL

    def _parse_answer(
        self, answer: str
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        """Parse the answer received from the server.

        Difference between apollo protocol and aws protocol:

        - aws protocol can return an error without an id
        - aws protocol will send start_ack messages

        Returns a list consisting of:
            - the answer_type:
              - 'connection_ack',
              - 'connection_error',
              - 'start_ack',
              - 'ka',
              - 'data',
              - 'error',
              - 'complete'
            - the answer id (Integer) if received or None
            - an execution Result if the answer_type is 'data' or None
        """

        answer_type: str = ""

        try:
            json_answer = json.loads(answer)

            answer_type = str(json_answer.get("type"))

            if answer_type == "start_ack":
                return ("start_ack", None, None)

            elif answer_type == "error" and "id" not in json_answer:
                error_payload = json_answer.get("payload")
                raise TransportServerError(f"Server error: '{error_payload!r}'")

            else:

                return WebsocketsTransport._parse_answer_apollo(
                    cast(WebsocketsTransport, self), json_answer
                )

        except ValueError:
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: {answer}"
            )

    async def _send_query(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> int:

        query_id = self.next_query_id

        self.next_query_id += 1

        data: Dict = {"query": print_ast(document)}

        if variable_values:
            data["variables"] = variable_values

        if operation_name:
            data["operationName"] = operation_name

        serialized_data = json.dumps(data, separators=(",", ":"))

        payload = {"data": serialized_data}

        message: Dict = {
            "id": str(query_id),
            "type": "start",
            "payload": payload,
        }

        assert self.auth is not None

        message["payload"]["extensions"] = {
            "authorization": self.auth.get_headers(serialized_data)
        }

        await self._send(
            json.dumps(
                message,
                separators=(",", ":"),
            )
        )

        return query_id

    subscribe = WebsocketsTransportBase.subscribe
    """Send a subscription query and receive the results using
    a python async generator.

    Only subscriptions are supported, queries and mutations are forbidden.

    The results are sent as an ExecutionResult object.
    """

    async def execute(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> ExecutionResult:
        """This method is not available.

        Only subscriptions are supported on the AWS realtime endpoint.

        :raise: AssertionError"""
        raise AssertionError(
            "execute method is not allowed for AppSyncWebsocketsTransport "
            "because only subscriptions are allowed on the realtime endpoint."
        )

    _initialize = WebsocketsTransport._initialize
    _stop_listener = WebsocketsTransport._send_stop_message  # type: ignore
    _send_init_message_and_wait_ack = (
        WebsocketsTransport._send_init_message_and_wait_ack
    )
    _wait_ack = WebsocketsTransport._wait_ack
