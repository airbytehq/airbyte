import asyncio
import json
import logging
from contextlib import suppress
from ssl import SSLContext
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from graphql import DocumentNode, ExecutionResult, print_ast
from websockets.datastructures import HeadersLike
from websockets.typing import Subprotocol

from .exceptions import (
    TransportProtocolError,
    TransportQueryError,
    TransportServerError,
)
from .websockets_base import WebsocketsTransportBase

log = logging.getLogger(__name__)


class WebsocketsTransport(WebsocketsTransportBase):
    """:ref:`Async Transport <async_transports>` used to execute GraphQL queries on
    remote servers with websocket connection.

    This transport uses asyncio and the websockets library in order to send requests
    on a websocket connection.
    """

    # This transport supports two subprotocols and will autodetect the
    # subprotocol supported on the server
    APOLLO_SUBPROTOCOL = cast(Subprotocol, "graphql-ws")
    GRAPHQLWS_SUBPROTOCOL = cast(Subprotocol, "graphql-transport-ws")

    def __init__(
        self,
        url: str,
        headers: Optional[HeadersLike] = None,
        ssl: Union[SSLContext, bool] = False,
        init_payload: Dict[str, Any] = {},
        connect_timeout: Optional[Union[int, float]] = 10,
        close_timeout: Optional[Union[int, float]] = 10,
        ack_timeout: Optional[Union[int, float]] = 10,
        keep_alive_timeout: Optional[Union[int, float]] = None,
        ping_interval: Optional[Union[int, float]] = None,
        pong_timeout: Optional[Union[int, float]] = None,
        answer_pings: bool = True,
        connect_args: Dict[str, Any] = {},
        subprotocols: Optional[List[Subprotocol]] = None,
    ) -> None:
        """Initialize the transport with the given parameters.

        :param url: The GraphQL server URL. Example: 'wss://server.com:PORT/graphql'.
        :param headers: Dict of HTTP Headers.
        :param ssl: ssl_context of the connection. Use ssl=False to disable encryption
        :param init_payload: Dict of the payload sent in the connection_init message.
        :param connect_timeout: Timeout in seconds for the establishment
            of the websocket connection. If None is provided this will wait forever.
        :param close_timeout: Timeout in seconds for the close. If None is provided
            this will wait forever.
        :param ack_timeout: Timeout in seconds to wait for the connection_ack message
            from the server. If None is provided this will wait forever.
        :param keep_alive_timeout: Optional Timeout in seconds to receive
            a sign of liveness from the server.
        :param ping_interval: Delay in seconds between pings sent by the client to
            the backend for the graphql-ws protocol. None (by default) means that
            we don't send pings. Note: there are also pings sent by the underlying
            websockets protocol. See the
            :ref:`keepalive documentation <websockets_transport_keepalives>`
            for more information about this.
        :param pong_timeout: Delay in seconds to receive a pong from the backend
            after we sent a ping (only for the graphql-ws protocol).
            By default equal to half of the ping_interval.
        :param answer_pings: Whether the client answers the pings from the backend
            (for the graphql-ws protocol).
            By default: True
        :param connect_args: Other parameters forwarded to
            `websockets.connect <https://websockets.readthedocs.io/en/stable/reference/\
            client.html#opening-a-connection>`_
        :param subprotocols: list of subprotocols sent to the
            backend in the 'subprotocols' http header.
            By default: both apollo and graphql-ws subprotocols.
        """

        super().__init__(
            url,
            headers,
            ssl,
            init_payload,
            connect_timeout,
            close_timeout,
            ack_timeout,
            keep_alive_timeout,
            connect_args,
        )

        self.ping_interval: Optional[Union[int, float]] = ping_interval
        self.pong_timeout: Optional[Union[int, float]]
        self.answer_pings: bool = answer_pings

        if ping_interval is not None:
            if pong_timeout is None:
                self.pong_timeout = ping_interval / 2
            else:
                self.pong_timeout = pong_timeout

        self.send_ping_task: Optional[asyncio.Future] = None

        self.ping_received: asyncio.Event = asyncio.Event()
        """ping_received is an asyncio Event which will fire  each time
        a ping is received with the graphql-ws protocol"""

        self.pong_received: asyncio.Event = asyncio.Event()
        """pong_received is an asyncio Event which will fire  each time
        a pong is received with the graphql-ws protocol"""

        if subprotocols is None:
            self.supported_subprotocols = [
                self.APOLLO_SUBPROTOCOL,
                self.GRAPHQLWS_SUBPROTOCOL,
            ]
        else:
            self.supported_subprotocols = subprotocols

    async def _wait_ack(self) -> None:
        """Wait for the connection_ack message. Keep alive messages are ignored"""

        while True:
            init_answer = await self._receive()

            answer_type, answer_id, execution_result = self._parse_answer(init_answer)

            if answer_type == "connection_ack":
                return

            if answer_type != "ka":
                raise TransportProtocolError(
                    "Websocket server did not return a connection ack"
                )

    async def _send_init_message_and_wait_ack(self) -> None:
        """Send init message to the provided websocket and wait for the connection ACK.

        If the answer is not a connection_ack message, we will return an Exception.
        """

        init_message = json.dumps(
            {"type": "connection_init", "payload": self.init_payload}
        )

        await self._send(init_message)

        # Wait for the connection_ack message or raise a TimeoutError
        await asyncio.wait_for(self._wait_ack(), self.ack_timeout)

    async def _initialize(self):
        await self._send_init_message_and_wait_ack()

    async def send_ping(self, payload: Optional[Any] = None) -> None:
        """Send a ping message for the graphql-ws protocol"""

        ping_message = {"type": "ping"}

        if payload is not None:
            ping_message["payload"] = payload

        await self._send(json.dumps(ping_message))

    async def send_pong(self, payload: Optional[Any] = None) -> None:
        """Send a pong message for the graphql-ws protocol"""

        pong_message = {"type": "pong"}

        if payload is not None:
            pong_message["payload"] = payload

        await self._send(json.dumps(pong_message))

    async def _send_stop_message(self, query_id: int) -> None:
        """Send stop message to the provided websocket connection and query_id.

        The server should afterwards return a 'complete' message.
        """

        stop_message = json.dumps({"id": str(query_id), "type": "stop"})

        await self._send(stop_message)

    async def _send_complete_message(self, query_id: int) -> None:
        """Send a complete message for the provided query_id.

        This is only for the graphql-ws protocol.
        """

        complete_message = json.dumps({"id": str(query_id), "type": "complete"})

        await self._send(complete_message)

    async def _stop_listener(self, query_id: int):
        """Stop the listener corresponding to the query_id depending on the
        detected backend protocol.

        For apollo: send a "stop" message
                    (a "complete" message will be sent from the backend)

        For graphql-ws: send a "complete" message and simulate the reception
                        of a "complete" message from the backend
        """
        log.debug(f"stop listener {query_id}")

        if self.subprotocol == self.GRAPHQLWS_SUBPROTOCOL:
            await self._send_complete_message(query_id)
            await self.listeners[query_id].put(("complete", None))
        else:
            await self._send_stop_message(query_id)

    async def _send_connection_terminate_message(self) -> None:
        """Send a connection_terminate message to the provided websocket connection.

        This message indicates that the connection will disconnect.
        """

        connection_terminate_message = json.dumps({"type": "connection_terminate"})

        await self._send(connection_terminate_message)

    async def _send_query(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> int:
        """Send a query to the provided websocket connection.

        We use an incremented id to reference the query.

        Returns the used id for this query.
        """

        query_id = self.next_query_id
        self.next_query_id += 1

        payload: Dict[str, Any] = {"query": print_ast(document)}
        if variable_values:
            payload["variables"] = variable_values
        if operation_name:
            payload["operationName"] = operation_name

        query_type = "start"

        if self.subprotocol == self.GRAPHQLWS_SUBPROTOCOL:
            query_type = "subscribe"

        query_str = json.dumps(
            {"id": str(query_id), "type": query_type, "payload": payload}
        )

        await self._send(query_str)

        return query_id

    async def _connection_terminate(self):
        if self.subprotocol == self.APOLLO_SUBPROTOCOL:
            await self._send_connection_terminate_message()

    def _parse_answer_graphqlws(
        self, json_answer: Dict[str, Any]
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        """Parse the answer received from the server if the server supports the
        graphql-ws protocol.

        Returns a list consisting of:
            - the answer_type (between:
              'connection_ack', 'ping', 'pong', 'data', 'error', 'complete')
            - the answer id (Integer) if received or None
            - an execution Result if the answer_type is 'data' or None

        Differences with the apollo websockets protocol (superclass):
            - the "data" message is now called "next"
            - the "stop" message is now called "complete"
            - there is no connection_terminate or connection_error messages
            - instead of a unidirectional keep-alive (ka) message from server to client,
              there is now the possibility to send bidirectional ping/pong messages
            - connection_ack has an optional payload
            - the 'error' answer type returns a list of errors instead of a single error
        """

        answer_type: str = ""
        answer_id: Optional[int] = None
        execution_result: Optional[ExecutionResult] = None

        try:
            answer_type = str(json_answer.get("type"))

            if answer_type in ["next", "error", "complete"]:
                answer_id = int(str(json_answer.get("id")))

                if answer_type == "next" or answer_type == "error":

                    payload = json_answer.get("payload")

                    if answer_type == "next":

                        if not isinstance(payload, dict):
                            raise ValueError("payload is not a dict")

                        if "errors" not in payload and "data" not in payload:
                            raise ValueError(
                                "payload does not contain 'data' or 'errors' fields"
                            )

                        execution_result = ExecutionResult(
                            errors=payload.get("errors"),
                            data=payload.get("data"),
                            extensions=payload.get("extensions"),
                        )

                        # Saving answer_type as 'data' to be understood with superclass
                        answer_type = "data"

                    elif answer_type == "error":

                        if not isinstance(payload, list):
                            raise ValueError("payload is not a list")

                        raise TransportQueryError(
                            str(payload[0]), query_id=answer_id, errors=payload
                        )

            elif answer_type in ["ping", "pong", "connection_ack"]:
                self.payloads[answer_type] = json_answer.get("payload", None)

            else:
                raise ValueError

            if self.check_keep_alive_task is not None:
                self._next_keep_alive_message.set()

        except ValueError as e:
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: {json_answer}"
            ) from e

        return answer_type, answer_id, execution_result

    def _parse_answer_apollo(
        self, json_answer: Dict[str, Any]
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        """Parse the answer received from the server if the server supports the
        apollo websockets protocol.

        Returns a list consisting of:
            - the answer_type (between:
              'connection_ack', 'ka', 'connection_error', 'data', 'error', 'complete')
            - the answer id (Integer) if received or None
            - an execution Result if the answer_type is 'data' or None
        """

        answer_type: str = ""
        answer_id: Optional[int] = None
        execution_result: Optional[ExecutionResult] = None

        try:
            answer_type = str(json_answer.get("type"))

            if answer_type in ["data", "error", "complete"]:
                answer_id = int(str(json_answer.get("id")))

                if answer_type == "data" or answer_type == "error":

                    payload = json_answer.get("payload")

                    if not isinstance(payload, dict):
                        raise ValueError("payload is not a dict")

                    if answer_type == "data":

                        if "errors" not in payload and "data" not in payload:
                            raise ValueError(
                                "payload does not contain 'data' or 'errors' fields"
                            )

                        execution_result = ExecutionResult(
                            errors=payload.get("errors"),
                            data=payload.get("data"),
                            extensions=payload.get("extensions"),
                        )

                    elif answer_type == "error":

                        raise TransportQueryError(
                            str(payload), query_id=answer_id, errors=[payload]
                        )

            elif answer_type == "ka":
                # Keep-alive message
                if self.check_keep_alive_task is not None:
                    self._next_keep_alive_message.set()
            elif answer_type == "connection_ack":
                pass
            elif answer_type == "connection_error":
                error_payload = json_answer.get("payload")
                raise TransportServerError(f"Server error: '{repr(error_payload)}'")
            else:
                raise ValueError

        except ValueError as e:
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: {json_answer}"
            ) from e

        return answer_type, answer_id, execution_result

    def _parse_answer(
        self, answer: str
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        """Parse the answer received from the server depending on
        the detected subprotocol.
        """
        try:
            json_answer = json.loads(answer)
        except ValueError:
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: {answer}"
            )

        if self.subprotocol == self.GRAPHQLWS_SUBPROTOCOL:
            return self._parse_answer_graphqlws(json_answer)

        return self._parse_answer_apollo(json_answer)

    async def _send_ping_coro(self) -> None:
        """Coroutine to periodically send a ping from the client to the backend.

        Only used for the graphql-ws protocol.

        Send a ping every ping_interval seconds.
        Close the connection if a pong is not received within pong_timeout seconds.
        """

        assert self.ping_interval is not None

        try:
            while True:
                await asyncio.sleep(self.ping_interval)

                await self.send_ping()

                await asyncio.wait_for(self.pong_received.wait(), self.pong_timeout)

                # Reset for the next iteration
                self.pong_received.clear()

        except asyncio.TimeoutError:
            # No pong received in the appriopriate time, close with error
            # If the timeout happens during a close already in progress, do nothing
            if self.close_task is None:
                await self._fail(
                    TransportServerError(
                        f"No pong received after {self.pong_timeout!r} seconds"
                    ),
                    clean_close=False,
                )

    async def _handle_answer(
        self,
        answer_type: str,
        answer_id: Optional[int],
        execution_result: Optional[ExecutionResult],
    ) -> None:

        # Put the answer in the queue
        await super()._handle_answer(answer_type, answer_id, execution_result)

        # Answer pong to ping for graphql-ws protocol
        if answer_type == "ping":
            self.ping_received.set()
            if self.answer_pings:
                await self.send_pong()

        elif answer_type == "pong":
            self.pong_received.set()

    async def _after_connect(self):

        # Find the backend subprotocol returned in the response headers
        response_headers = self.websocket.response_headers
        try:
            self.subprotocol = response_headers["Sec-WebSocket-Protocol"]
        except KeyError:
            # If the server does not send the subprotocol header, using
            # the apollo subprotocol by default
            self.subprotocol = self.APOLLO_SUBPROTOCOL

        log.debug(f"backend subprotocol returned: {self.subprotocol!r}")

    async def _after_initialize(self):

        # If requested, create a task to send periodic pings to the backend
        if (
            self.subprotocol == self.GRAPHQLWS_SUBPROTOCOL
            and self.ping_interval is not None
        ):

            self.send_ping_task = asyncio.ensure_future(self._send_ping_coro())

    async def _close_hook(self):

        # Properly shut down the send ping task if enabled
        if self.send_ping_task is not None:
            self.send_ping_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.send_ping_task
            self.send_ping_task = None
