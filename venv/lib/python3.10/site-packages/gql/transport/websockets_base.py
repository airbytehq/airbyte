import asyncio
import logging
import warnings
from abc import abstractmethod
from contextlib import suppress
from ssl import SSLContext
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union, cast

import websockets
from graphql import DocumentNode, ExecutionResult
from websockets.client import WebSocketClientProtocol
from websockets.datastructures import Headers, HeadersLike
from websockets.exceptions import ConnectionClosed
from websockets.typing import Data, Subprotocol

from .async_transport import AsyncTransport
from .exceptions import (
    TransportAlreadyConnected,
    TransportClosed,
    TransportProtocolError,
    TransportQueryError,
    TransportServerError,
)

log = logging.getLogger("gql.transport.websockets")

ParsedAnswer = Tuple[str, Optional[ExecutionResult]]


class ListenerQueue:
    """Special queue used for each query waiting for server answers

    If the server is stopped while the listener is still waiting,
    Then we send an exception to the queue and this exception will be raised
    to the consumer once all the previous messages have been consumed from the queue
    """

    def __init__(self, query_id: int, send_stop: bool) -> None:
        self.query_id: int = query_id
        self.send_stop: bool = send_stop
        self._queue: asyncio.Queue = asyncio.Queue()
        self._closed: bool = False

    async def get(self) -> ParsedAnswer:

        try:
            item = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            item = await self._queue.get()

        self._queue.task_done()

        # If we receive an exception when reading the queue, we raise it
        if isinstance(item, Exception):
            self._closed = True
            raise item

        # Don't need to save new answers or
        # send the stop message if we already received the complete message
        answer_type, execution_result = item
        if answer_type == "complete":
            self.send_stop = False
            self._closed = True

        return item

    async def put(self, item: ParsedAnswer) -> None:

        if not self._closed:
            await self._queue.put(item)

    async def set_exception(self, exception: Exception) -> None:

        # Put the exception in the queue
        await self._queue.put(exception)

        # Don't need to send stop messages in case of error
        self.send_stop = False
        self._closed = True


class WebsocketsTransportBase(AsyncTransport):
    """abstract :ref:`Async Transport <async_transports>` used to implement
    different websockets protocols.

    This transport uses asyncio and the websockets library in order to send requests
    on a websocket connection.
    """

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
        connect_args: Dict[str, Any] = {},
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
        :param connect_args: Other parameters forwarded to websockets.connect
        """

        self.url: str = url
        self.headers: Optional[HeadersLike] = headers
        self.ssl: Union[SSLContext, bool] = ssl
        self.init_payload: Dict[str, Any] = init_payload

        self.connect_timeout: Optional[Union[int, float]] = connect_timeout
        self.close_timeout: Optional[Union[int, float]] = close_timeout
        self.ack_timeout: Optional[Union[int, float]] = ack_timeout
        self.keep_alive_timeout: Optional[Union[int, float]] = keep_alive_timeout

        self.connect_args = connect_args

        self.websocket: Optional[WebSocketClientProtocol] = None
        self.next_query_id: int = 1
        self.listeners: Dict[int, ListenerQueue] = {}

        self.receive_data_task: Optional[asyncio.Future] = None
        self.check_keep_alive_task: Optional[asyncio.Future] = None
        self.close_task: Optional[asyncio.Future] = None

        # We need to set an event loop here if there is none
        # Or else we will not be able to create an asyncio.Event()
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", message="There is no current event loop"
                )
                self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        self._wait_closed: asyncio.Event = asyncio.Event()
        self._wait_closed.set()

        self._no_more_listeners: asyncio.Event = asyncio.Event()
        self._no_more_listeners.set()

        if self.keep_alive_timeout is not None:
            self._next_keep_alive_message: asyncio.Event = asyncio.Event()
            self._next_keep_alive_message.set()

        self.payloads: Dict[str, Any] = {}
        """payloads is a dict which will contain the payloads received
        for example with the graphql-ws protocol: 'ping', 'pong', 'connection_ack'"""

        self._connecting: bool = False

        self.close_exception: Optional[Exception] = None

        # The list of supported subprotocols should be defined in the subclass
        self.supported_subprotocols: List[Subprotocol] = []

        self.response_headers: Optional[Headers] = None

    async def _initialize(self):
        """Hook to send the initialization messages after the connection
        and potentially wait for the backend ack.
        """
        pass  # pragma: no cover

    async def _stop_listener(self, query_id: int):
        """Hook to stop to listen to a specific query.
        Will send a stop message in some subclasses.
        """
        pass  # pragma: no cover

    async def _after_connect(self):
        """Hook to add custom code for subclasses after the connection
        has been established.
        """
        pass  # pragma: no cover

    async def _after_initialize(self):
        """Hook to add custom code for subclasses after the initialization
        has been done.
        """
        pass  # pragma: no cover

    async def _close_hook(self):
        """Hook to add custom code for subclasses for the connection close"""
        pass  # pragma: no cover

    async def _connection_terminate(self):
        """Hook to add custom code for subclasses after the initialization
        has been done.
        """
        pass  # pragma: no cover

    async def _send(self, message: str) -> None:
        """Send the provided message to the websocket connection and log the message"""

        if not self.websocket:
            raise TransportClosed(
                "Transport is not connected"
            ) from self.close_exception

        try:
            await self.websocket.send(message)
            log.info(">>> %s", message)
        except ConnectionClosed as e:
            await self._fail(e, clean_close=False)
            raise e

    async def _receive(self) -> str:
        """Wait the next message from the websocket connection and log the answer"""

        # It is possible that the websocket has been already closed in another task
        if self.websocket is None:
            raise TransportClosed("Transport is already closed")

        # Wait for the next websocket frame. Can raise ConnectionClosed
        data: Data = await self.websocket.recv()

        # websocket.recv() can return either str or bytes
        # In our case, we should receive only str here
        if not isinstance(data, str):
            raise TransportProtocolError("Binary data received in the websocket")

        answer: str = data

        log.info("<<< %s", answer)

        return answer

    @abstractmethod
    async def _send_query(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> int:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _parse_answer(
        self, answer: str
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        raise NotImplementedError  # pragma: no cover

    async def _check_ws_liveness(self) -> None:
        """Coroutine which will periodically check the liveness of the connection
        through keep-alive messages
        """

        try:
            while True:
                await asyncio.wait_for(
                    self._next_keep_alive_message.wait(), self.keep_alive_timeout
                )

                # Reset for the next iteration
                self._next_keep_alive_message.clear()

        except asyncio.TimeoutError:
            # No keep-alive message in the appriopriate interval, close with error
            # while trying to notify the server of a proper close (in case
            # the keep-alive interval of the client or server was not aligned
            # the connection still remains)

            # If the timeout happens during a close already in progress, do nothing
            if self.close_task is None:
                await self._fail(
                    TransportServerError(
                        "No keep-alive message has been received within "
                        "the expected interval ('keep_alive_timeout' parameter)"
                    ),
                    clean_close=False,
                )

        except asyncio.CancelledError:
            # The client is probably closing, handle it properly
            pass

    async def _receive_data_loop(self) -> None:
        """Main asyncio task which will listen to the incoming messages and will
        call the parse_answer and handle_answer methods of the subclass."""
        try:
            while True:

                # Wait the next answer from the websocket server
                try:
                    answer = await self._receive()
                except (ConnectionClosed, TransportProtocolError) as e:
                    await self._fail(e, clean_close=False)
                    break
                except TransportClosed:
                    break

                # Parse the answer
                try:
                    answer_type, answer_id, execution_result = self._parse_answer(
                        answer
                    )
                except TransportQueryError as e:
                    # Received an exception for a specific query
                    # ==> Add an exception to this query queue
                    # The exception is raised for this specific query,
                    # but the transport is not closed.
                    assert isinstance(
                        e.query_id, int
                    ), "TransportQueryError should have a query_id defined here"
                    try:
                        await self.listeners[e.query_id].set_exception(e)
                    except KeyError:
                        # Do nothing if no one is listening to this query_id
                        pass

                    continue

                except (TransportServerError, TransportProtocolError) as e:
                    # Received a global exception for this transport
                    # ==> close the transport
                    # The exception will be raised for all current queries.
                    await self._fail(e, clean_close=False)
                    break

                await self._handle_answer(answer_type, answer_id, execution_result)

        finally:
            log.debug("Exiting _receive_data_loop()")

    async def _handle_answer(
        self,
        answer_type: str,
        answer_id: Optional[int],
        execution_result: Optional[ExecutionResult],
    ) -> None:

        try:
            # Put the answer in the queue
            if answer_id is not None:
                await self.listeners[answer_id].put((answer_type, execution_result))
        except KeyError:
            # Do nothing if no one is listening to this query_id.
            pass

    async def subscribe(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        send_stop: Optional[bool] = True,
    ) -> AsyncGenerator[ExecutionResult, None]:
        """Send a query and receive the results using a python async generator.

        The query can be a graphql query, mutation or subscription.

        The results are sent as an ExecutionResult object.
        """

        # Send the query and receive the id
        query_id: int = await self._send_query(
            document, variable_values, operation_name
        )

        # Create a queue to receive the answers for this query_id
        listener = ListenerQueue(query_id, send_stop=(send_stop is True))
        self.listeners[query_id] = listener

        # We will need to wait at close for this query to clean properly
        self._no_more_listeners.clear()

        try:
            # Loop over the received answers
            while True:

                # Wait for the answer from the queue of this query_id
                # This can raise a TransportError or ConnectionClosed exception.
                answer_type, execution_result = await listener.get()

                # If the received answer contains data,
                # Then we will yield the results back as an ExecutionResult object
                if execution_result is not None:
                    yield execution_result

                # If we receive a 'complete' answer from the server,
                # Then we will end this async generator output without errors
                elif answer_type == "complete":
                    log.debug(
                        f"Complete received for query {query_id} --> exit without error"
                    )
                    break

        except (asyncio.CancelledError, GeneratorExit) as e:
            log.debug(f"Exception in subscribe: {e!r}")
            if listener.send_stop:
                await self._stop_listener(query_id)
                listener.send_stop = False

        finally:
            log.debug(f"In subscribe finally for query_id {query_id}")
            self._remove_listener(query_id)

    async def execute(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute the provided document AST against the configured remote server
        using the current session.

        Send a query but close the async generator as soon as we have the first answer.

        The result is sent as an ExecutionResult object.
        """
        first_result = None

        generator = self.subscribe(
            document, variable_values, operation_name, send_stop=False
        )

        async for result in generator:
            first_result = result

            # Note: we need to run generator.aclose() here or the finally block in
            # the subscribe will not be reached in pypy3 (python version 3.6.1)
            await generator.aclose()

            break

        if first_result is None:
            raise TransportQueryError(
                "Query completed without any answer received from the server"
            )

        return first_result

    async def connect(self) -> None:
        """Coroutine which will:

        - connect to the websocket address
        - send the init message
        - wait for the connection acknowledge from the server
        - create an asyncio task which will be used to receive
          and parse the websocket answers

        Should be cleaned with a call to the close coroutine
        """

        log.debug("connect: starting")

        if self.websocket is None and not self._connecting:

            # Set connecting to True to avoid a race condition if user is trying
            # to connect twice using the same client at the same time
            self._connecting = True

            # If the ssl parameter is not provided,
            # generate the ssl value depending on the url
            ssl: Optional[Union[SSLContext, bool]]
            if self.ssl:
                ssl = self.ssl
            else:
                ssl = True if self.url.startswith("wss") else None

            # Set default arguments used in the websockets.connect call
            connect_args: Dict[str, Any] = {
                "ssl": ssl,
                "extra_headers": self.headers,
                "subprotocols": self.supported_subprotocols,
            }

            # Adding custom parameters passed from init
            connect_args.update(self.connect_args)

            # Connection to the specified url
            # Generate a TimeoutError if taking more than connect_timeout seconds
            # Set the _connecting flag to False after in all cases
            try:
                self.websocket = await asyncio.wait_for(
                    websockets.client.connect(self.url, **connect_args),
                    self.connect_timeout,
                )
            finally:
                self._connecting = False

            self.websocket = cast(WebSocketClientProtocol, self.websocket)

            self.response_headers = self.websocket.response_headers

            # Run the after_connect hook of the subclass
            await self._after_connect()

            self.next_query_id = 1
            self.close_exception = None
            self._wait_closed.clear()

            # Send the init message and wait for the ack from the server
            # Note: This should generate a TimeoutError
            # if no ACKs are received within the ack_timeout
            try:
                await self._initialize()
            except ConnectionClosed as e:
                raise e
            except (TransportProtocolError, asyncio.TimeoutError) as e:
                await self._fail(e, clean_close=False)
                raise e

            # Run the after_init hook of the subclass
            await self._after_initialize()

            # If specified, create a task to check liveness of the connection
            # through keep-alive messages
            if self.keep_alive_timeout is not None:
                self.check_keep_alive_task = asyncio.ensure_future(
                    self._check_ws_liveness()
                )

            # Create a task to listen to the incoming websocket messages
            self.receive_data_task = asyncio.ensure_future(self._receive_data_loop())

        else:
            raise TransportAlreadyConnected("Transport is already connected")

        log.debug("connect: done")

    def _remove_listener(self, query_id) -> None:
        """After exiting from a subscription, remove the listener and
        signal an event if this was the last listener for the client.
        """
        if query_id in self.listeners:
            del self.listeners[query_id]

        remaining = len(self.listeners)
        log.debug(f"listener {query_id} deleted, {remaining} remaining")

        if remaining == 0:
            self._no_more_listeners.set()

    async def _clean_close(self, e: Exception) -> None:
        """Coroutine which will:

        - send stop messages for each active subscription to the server
        - send the connection terminate message
        """

        # Send 'stop' message for all current queries
        for query_id, listener in self.listeners.items():

            if listener.send_stop:
                await self._stop_listener(query_id)
                listener.send_stop = False

        # Wait that there is no more listeners (we received 'complete' for all queries)
        try:
            await asyncio.wait_for(self._no_more_listeners.wait(), self.close_timeout)
        except asyncio.TimeoutError:  # pragma: no cover
            log.debug("Timer close_timeout fired")

        # Calling the subclass hook
        await self._connection_terminate()

    async def _close_coro(self, e: Exception, clean_close: bool = True) -> None:
        """Coroutine which will:

        - do a clean_close if possible:
            - send stop messages for each active query to the server
            - send the connection terminate message
        - close the websocket connection
        - send the exception to all the remaining listeners
        """

        log.debug("_close_coro: starting")

        try:

            # We should always have an active websocket connection here
            assert self.websocket is not None

            # Properly shut down liveness checker if enabled
            if self.check_keep_alive_task is not None:
                # More info: https://stackoverflow.com/a/43810272/1113207
                self.check_keep_alive_task.cancel()
                with suppress(asyncio.CancelledError):
                    await self.check_keep_alive_task

            # Calling the subclass close hook
            await self._close_hook()

            # Saving exception to raise it later if trying to use the transport
            # after it has already closed.
            self.close_exception = e

            if clean_close:
                log.debug("_close_coro: starting clean_close")
                try:
                    await self._clean_close(e)
                except Exception as exc:  # pragma: no cover
                    log.warning("Ignoring exception in _clean_close: " + repr(exc))

            log.debug("_close_coro: sending exception to listeners")

            # Send an exception to all remaining listeners
            for query_id, listener in self.listeners.items():
                await listener.set_exception(e)

            log.debug("_close_coro: close websocket connection")

            await self.websocket.close()

            log.debug("_close_coro: websocket connection closed")

        except Exception as exc:  # pragma: no cover
            log.warning("Exception catched in _close_coro: " + repr(exc))

        finally:

            log.debug("_close_coro: start cleanup")

            self.websocket = None
            self.close_task = None
            self.check_keep_alive_task = None
            self._wait_closed.set()

        log.debug("_close_coro: exiting")

    async def _fail(self, e: Exception, clean_close: bool = True) -> None:
        log.debug("_fail: starting with exception: " + repr(e))

        if self.close_task is None:

            if self.websocket is None:
                log.debug("_fail started with self.websocket == None -> already closed")
            else:
                self.close_task = asyncio.shield(
                    asyncio.ensure_future(self._close_coro(e, clean_close=clean_close))
                )
        else:
            log.debug(
                "close_task is not None in _fail. Previous exception is: "
                + repr(self.close_exception)
                + " New exception is: "
                + repr(e)
            )

    async def close(self) -> None:
        log.debug("close: starting")

        await self._fail(TransportClosed("Websocket GraphQL transport closed by user"))
        await self.wait_closed()

        log.debug("close: done")

    async def wait_closed(self) -> None:
        log.debug("wait_close: starting")

        await self._wait_closed.wait()

        log.debug("wait_close: done")
