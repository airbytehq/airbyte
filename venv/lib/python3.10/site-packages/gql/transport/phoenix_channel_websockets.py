import asyncio
import json
import logging
from typing import Any, Dict, Optional, Tuple

from graphql import DocumentNode, ExecutionResult, print_ast
from websockets.exceptions import ConnectionClosed

from .exceptions import (
    TransportProtocolError,
    TransportQueryError,
    TransportServerError,
)
from .websockets_base import WebsocketsTransportBase

log = logging.getLogger(__name__)


class Subscription:
    """Records listener_id and unsubscribe query_id for a subscription."""

    def __init__(self, query_id: int) -> None:
        self.listener_id: int = query_id
        self.unsubscribe_id: Optional[int] = None


class PhoenixChannelWebsocketsTransport(WebsocketsTransportBase):
    """The PhoenixChannelWebsocketsTransport is an async transport
    which allows you to execute queries and subscriptions against an `Absinthe`_
    backend using the `Phoenix`_ framework `channels`_.

    .. _Absinthe: http://absinthe-graphql.org
    .. _Phoenix: https://www.phoenixframework.org
    .. _channels: https://hexdocs.pm/phoenix/Phoenix.Channel.html#content
    """

    def __init__(
        self,
        channel_name: str = "__absinthe__:control",
        heartbeat_interval: float = 30,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the transport with the given parameters.

        :param channel_name: Channel on the server this transport will join.
            The default for Absinthe servers is "__absinthe__:control"
        :param heartbeat_interval: Interval in second between each heartbeat messages
            sent by the client
        """
        self.channel_name: str = channel_name
        self.heartbeat_interval: float = heartbeat_interval
        self.heartbeat_task: Optional[asyncio.Future] = None
        self.subscriptions: Dict[str, Subscription] = {}
        super(PhoenixChannelWebsocketsTransport, self).__init__(*args, **kwargs)

    async def _initialize(self) -> None:
        """Join the specified channel and wait for the connection ACK.

        If the answer is not a connection_ack message, we will return an Exception.
        """

        query_id = self.next_query_id
        self.next_query_id += 1

        init_message = json.dumps(
            {
                "topic": self.channel_name,
                "event": "phx_join",
                "payload": {},
                "ref": query_id,
            }
        )

        await self._send(init_message)

        # Wait for the connection_ack message or raise a TimeoutError
        init_answer = await asyncio.wait_for(self._receive(), self.ack_timeout)

        answer_type, answer_id, execution_result = self._parse_answer(init_answer)

        if answer_type != "reply":
            raise TransportProtocolError(
                "Websocket server did not return a connection ack"
            )

        async def heartbeat_coro():
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                try:
                    query_id = self.next_query_id
                    self.next_query_id += 1

                    await self._send(
                        json.dumps(
                            {
                                "topic": "phoenix",
                                "event": "heartbeat",
                                "payload": {},
                                "ref": query_id,
                            }
                        )
                    )
                except ConnectionClosed:  # pragma: no cover
                    return

        self.heartbeat_task = asyncio.ensure_future(heartbeat_coro())

    async def _send_stop_message(self, query_id: int) -> None:
        """Send an 'unsubscribe' message to the Phoenix Channel referencing
        the listener's query_id, saving the query_id of the message.

        The server should afterwards return a 'phx_reply' message with
        the same query_id and subscription_id of the 'unsubscribe' request.
        """
        subscription_id = self._find_existing_subscription(query_id)

        unsubscribe_query_id = self.next_query_id
        self.next_query_id += 1

        # Save the ref so it can be matched in the reply
        self.subscriptions[subscription_id].unsubscribe_id = unsubscribe_query_id
        unsubscribe_message = json.dumps(
            {
                "topic": self.channel_name,
                "event": "unsubscribe",
                "payload": {"subscriptionId": subscription_id},
                "ref": unsubscribe_query_id,
            }
        )

        await self._send(unsubscribe_message)

    async def _stop_listener(self, query_id: int) -> None:
        await self._send_stop_message(query_id)

    async def _send_connection_terminate_message(self) -> None:
        """Send a phx_leave message to disconnect from the provided channel."""

        query_id = self.next_query_id
        self.next_query_id += 1

        connection_terminate_message = json.dumps(
            {
                "topic": self.channel_name,
                "event": "phx_leave",
                "payload": {},
                "ref": query_id,
            }
        )

        await self._send(connection_terminate_message)

    async def _connection_terminate(self):
        await self._send_connection_terminate_message()

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

        query_str = json.dumps(
            {
                "topic": self.channel_name,
                "event": "doc",
                "payload": {
                    "query": print_ast(document),
                    "variables": variable_values or {},
                },
                "ref": query_id,
            }
        )

        await self._send(query_str)

        return query_id

    def _parse_answer(
        self, answer: str
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        """Parse the answer received from the server

        Returns a list consisting of:
            - the answer_type (between:
              'data', 'reply', 'complete', 'close')
            - the answer id (Integer) if received or None
            - an execution Result if the answer_type is 'data' or None
        """

        event: str = ""
        answer_id: Optional[int] = None
        answer_type: str = ""
        execution_result: Optional[ExecutionResult] = None
        subscription_id: Optional[str] = None

        def _get_value(d: Any, key: str, label: str) -> Any:
            if not isinstance(d, dict):
                raise ValueError(f"{label} is not a dict")

            return d.get(key)

        def _required_value(d: Any, key: str, label: str) -> Any:
            value = _get_value(d, key, label)
            if value is None:
                raise ValueError(f"null {key} in {label}")

            return value

        def _required_subscription_id(
            d: Any, label: str, must_exist: bool = False, must_not_exist=False
        ) -> str:
            subscription_id = str(_required_value(d, "subscriptionId", label))
            if must_exist and (subscription_id not in self.subscriptions):
                raise ValueError("unregistered subscriptionId")
            if must_not_exist and (subscription_id in self.subscriptions):
                raise ValueError("previously registered subscriptionId")

            return subscription_id

        def _validate_data_response(d: Any, label: str) -> dict:
            """Make sure query, mutation or subscription answer conforms.
            The GraphQL spec says only three keys are permitted.
            """
            if not isinstance(d, dict):
                raise ValueError(f"{label} is not a dict")

            keys = set(d.keys())
            invalid = keys - {"data", "errors", "extensions"}
            if len(invalid) > 0:
                raise ValueError(
                    f"{label} contains invalid items: " + ", ".join(invalid)
                )
            return d

        try:
            json_answer = json.loads(answer)

            event = str(_required_value(json_answer, "event", "answer"))

            if event == "subscription:data":
                payload = _required_value(json_answer, "payload", "answer")

                subscription_id = _required_subscription_id(
                    payload, "payload", must_exist=True
                )

                result = _validate_data_response(payload.get("result"), "result")

                answer_type = "data"

                subscription = self.subscriptions[subscription_id]
                answer_id = subscription.listener_id

                execution_result = ExecutionResult(
                    data=result.get("data"),
                    errors=result.get("errors"),
                    extensions=result.get("extensions"),
                )

            elif event == "phx_reply":

                # Will generate a ValueError if 'ref' is not there
                # or if it is not an integer
                answer_id = int(_required_value(json_answer, "ref", "answer"))

                payload = _required_value(json_answer, "payload", "answer")

                status = _get_value(payload, "status", "payload")

                if status == "ok":
                    answer_type = "reply"

                    if answer_id in self.listeners:
                        response = _required_value(payload, "response", "payload")

                        if isinstance(response, dict) and "subscriptionId" in response:

                            # Subscription answer
                            subscription_id = _required_subscription_id(
                                response, "response", must_not_exist=True
                            )

                            self.subscriptions[subscription_id] = Subscription(
                                answer_id
                            )

                        else:
                            # Query or mutation answer
                            # GraphQL spec says only three keys are permitted
                            response = _validate_data_response(response, "response")

                            answer_type = "data"

                            execution_result = ExecutionResult(
                                data=response.get("data"),
                                errors=response.get("errors"),
                                extensions=response.get("extensions"),
                            )
                    else:
                        (
                            registered_subscription_id,
                            listener_id,
                        ) = self._find_subscription(answer_id)
                        if registered_subscription_id is not None:
                            # Unsubscription answer
                            response = _required_value(payload, "response", "payload")
                            subscription_id = _required_subscription_id(
                                response, "response"
                            )

                            if subscription_id != registered_subscription_id:
                                raise ValueError("subscription id does not match")

                            answer_type = "complete"

                            answer_id = listener_id

                elif status == "error":
                    response = payload.get("response")

                    if isinstance(response, dict):
                        if "errors" in response:
                            raise TransportQueryError(
                                str(response.get("errors")), query_id=answer_id
                            )
                        elif "reason" in response:
                            raise TransportQueryError(
                                str(response.get("reason")), query_id=answer_id
                            )
                    raise TransportQueryError("reply error", query_id=answer_id)

                elif status == "timeout":
                    raise TransportQueryError("reply timeout", query_id=answer_id)
                else:
                    # missing or unrecognized status, just continue
                    pass

            elif event == "phx_error":
                # Sent if the channel has crashed
                # answer_id will be the "join_ref" for the channel
                # answer_id = int(json_answer.get("ref"))
                raise TransportServerError("Server error")
            elif event == "phx_close":
                answer_type = "close"
            else:
                raise ValueError("unrecognized event")

        except ValueError as e:
            log.error(f"Error parsing answer '{answer}': {e!r}")
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: {e!s}"
            ) from e

        return answer_type, answer_id, execution_result

    async def _handle_answer(
        self,
        answer_type: str,
        answer_id: Optional[int],
        execution_result: Optional[ExecutionResult],
    ) -> None:
        if answer_type == "close":
            await self.close()
        else:
            await super()._handle_answer(answer_type, answer_id, execution_result)

    def _remove_listener(self, query_id: int) -> None:
        """If the listener was a subscription, remove that information."""
        try:
            subscription_id = self._find_existing_subscription(query_id)
            del self.subscriptions[subscription_id]
        except Exception:
            pass
        super()._remove_listener(query_id)

    def _find_subscription(self, query_id: int) -> Tuple[Optional[str], int]:
        """Perform a reverse lookup to find the subscription id matching
        a listener's query_id.
        """
        for subscription_id, subscription in self.subscriptions.items():
            if query_id == subscription.listener_id:
                return subscription_id, query_id
            if query_id == subscription.unsubscribe_id:
                return subscription_id, subscription.listener_id
        return None, query_id

    def _find_existing_subscription(self, query_id: int) -> str:
        """Perform a reverse lookup to find the subscription id matching
        a listener's query_id.
        """
        subscription_id, _listener_id = self._find_subscription(query_id)

        if subscription_id is None:
            raise TransportProtocolError(
                f"No subscription registered for listener {query_id}"
            )
        return subscription_id

    async def _close_coro(self, e: Exception, clean_close: bool = True) -> None:
        if self.heartbeat_task is not None:
            self.heartbeat_task.cancel()

        await super()._close_coro(e, clean_close)
