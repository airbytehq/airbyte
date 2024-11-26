import asyncio
import functools
import io
import json
import logging
from ssl import SSLContext
from typing import Any, AsyncGenerator, Callable, Dict, Optional, Tuple, Type, Union

import aiohttp
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.client_reqrep import Fingerprint
from aiohttp.helpers import BasicAuth
from aiohttp.typedefs import LooseCookies, LooseHeaders
from graphql import DocumentNode, ExecutionResult, print_ast
from multidict import CIMultiDictProxy

from ..utils import extract_files
from .appsync_auth import AppSyncAuthentication
from .async_transport import AsyncTransport
from .exceptions import (
    TransportAlreadyConnected,
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)

log = logging.getLogger(__name__)


class AIOHTTPTransport(AsyncTransport):
    """:ref:`Async Transport <async_transports>` to execute GraphQL queries
    on remote servers with an HTTP connection.

    This transport use the aiohttp library with asyncio.
    """

    file_classes: Tuple[Type[Any], ...] = (
        io.IOBase,
        aiohttp.StreamReader,
        AsyncGenerator,
    )

    def __init__(
        self,
        url: str,
        headers: Optional[LooseHeaders] = None,
        cookies: Optional[LooseCookies] = None,
        auth: Optional[Union[BasicAuth, "AppSyncAuthentication"]] = None,
        ssl: Union[SSLContext, bool, Fingerprint] = False,
        timeout: Optional[int] = None,
        ssl_close_timeout: Optional[Union[int, float]] = 10,
        json_serialize: Callable = json.dumps,
        client_session_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the transport with the given aiohttp parameters.

        :param url: The GraphQL server URL. Example: 'https://server.com:PORT/path'.
        :param headers: Dict of HTTP Headers.
        :param cookies: Dict of HTTP cookies.
        :param auth: BasicAuth object to enable Basic HTTP auth if needed
                     Or Appsync Authentication class
        :param ssl: ssl_context of the connection. Use ssl=False to disable encryption
        :param ssl_close_timeout: Timeout in seconds to wait for the ssl connection
                                  to close properly
        :param json_serialize: Json serializer callable.
                By default json.dumps() function
        :param client_session_args: Dict of extra args passed to
                `aiohttp.ClientSession`_

        .. _aiohttp.ClientSession:
          https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
        """
        self.url: str = url
        self.headers: Optional[LooseHeaders] = headers
        self.cookies: Optional[LooseCookies] = cookies
        self.auth: Optional[Union[BasicAuth, "AppSyncAuthentication"]] = auth
        self.ssl: Union[SSLContext, bool, Fingerprint] = ssl
        self.timeout: Optional[int] = timeout
        self.ssl_close_timeout: Optional[Union[int, float]] = ssl_close_timeout
        self.client_session_args = client_session_args
        self.session: Optional[aiohttp.ClientSession] = None
        self.response_headers: Optional[CIMultiDictProxy[str]]
        self.json_serialize: Callable = json_serialize

    async def connect(self) -> None:
        """Coroutine which will create an aiohttp ClientSession() as self.session.

        Don't call this coroutine directly on the transport, instead use
        :code:`async with` on the client and this coroutine will be executed
        to create the session.

        Should be cleaned with a call to the close coroutine.
        """

        if self.session is None:

            client_session_args: Dict[str, Any] = {
                "cookies": self.cookies,
                "headers": self.headers,
                "auth": None
                if isinstance(self.auth, AppSyncAuthentication)
                else self.auth,
                "json_serialize": self.json_serialize,
            }

            if self.timeout is not None:
                client_session_args["timeout"] = aiohttp.ClientTimeout(
                    total=self.timeout
                )

            # Adding custom parameters passed from init
            if self.client_session_args:
                client_session_args.update(self.client_session_args)  # type: ignore

            log.debug("Connecting transport")

            self.session = aiohttp.ClientSession(**client_session_args)

        else:
            raise TransportAlreadyConnected("Transport is already connected")

    @staticmethod
    def create_aiohttp_closed_event(session) -> asyncio.Event:
        """Work around aiohttp issue that doesn't properly close transports on exit.

        See https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-639080209

        Returns:
           An event that will be set once all transports have been properly closed.
        """

        ssl_transports = 0
        all_is_lost = asyncio.Event()

        def connection_lost(exc, orig_lost):
            nonlocal ssl_transports

            try:
                orig_lost(exc)
            finally:
                ssl_transports -= 1
                if ssl_transports == 0:
                    all_is_lost.set()

        def eof_received(orig_eof_received):
            try:
                orig_eof_received()
            except AttributeError:  # pragma: no cover
                # It may happen that eof_received() is called after
                # _app_protocol and _transport are set to None.
                pass

        for conn in session.connector._conns.values():
            for handler, _ in conn:
                proto = getattr(handler.transport, "_ssl_protocol", None)
                if proto is None:
                    continue

                ssl_transports += 1
                orig_lost = proto.connection_lost
                orig_eof_received = proto.eof_received

                proto.connection_lost = functools.partial(
                    connection_lost, orig_lost=orig_lost
                )
                proto.eof_received = functools.partial(
                    eof_received, orig_eof_received=orig_eof_received
                )

        if ssl_transports == 0:
            all_is_lost.set()

        return all_is_lost

    async def close(self) -> None:
        """Coroutine which will close the aiohttp session.

        Don't call this coroutine directly on the transport, instead use
        :code:`async with` on the client and this coroutine will be executed
        when you exit the async context manager.
        """
        if self.session is not None:

            log.debug("Closing transport")

            if (
                self.client_session_args
                and self.client_session_args.get("connector_owner") is False
            ):

                log.debug("connector_owner is False -> not closing connector")

            else:
                closed_event = self.create_aiohttp_closed_event(self.session)
                await self.session.close()
                try:
                    await asyncio.wait_for(closed_event.wait(), self.ssl_close_timeout)
                except asyncio.TimeoutError:
                    pass

        self.session = None

    async def execute(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        extra_args: Optional[Dict[str, Any]] = None,
        upload_files: bool = False,
    ) -> ExecutionResult:
        """Execute the provided document AST against the configured remote server
        using the current session.
        This uses the aiohttp library to perform a HTTP POST request asynchronously
        to the remote server.

        Don't call this coroutine directly on the transport, instead use
        :code:`execute` on a client or a session.

        :param document: the parsed GraphQL request
        :param variable_values: An optional Dict of variable values
        :param operation_name: An optional Operation name for the request
        :param extra_args: additional arguments to send to the aiohttp post method
        :param upload_files: Set to True if you want to put files in the variable values
        :returns: an ExecutionResult object.
        """

        query_str = print_ast(document)

        payload: Dict[str, Any] = {
            "query": query_str,
        }

        if operation_name:
            payload["operationName"] = operation_name

        if upload_files:

            # If the upload_files flag is set, then we need variable_values
            assert variable_values is not None

            # If we upload files, we will extract the files present in the
            # variable_values dict and replace them by null values
            nulled_variable_values, files = extract_files(
                variables=variable_values,
                file_classes=self.file_classes,
            )

            # Save the nulled variable values in the payload
            payload["variables"] = nulled_variable_values

            # Prepare aiohttp to send multipart-encoded data
            data = aiohttp.FormData()

            # Generate the file map
            # path is nested in a list because the spec allows multiple pointers
            # to the same file. But we don't support that.
            # Will generate something like {"0": ["variables.file"]}
            file_map = {str(i): [path] for i, path in enumerate(files)}

            # Enumerate the file streams
            # Will generate something like {'0': <_io.BufferedReader ...>}
            file_streams = {str(i): files[path] for i, path in enumerate(files)}

            # Add the payload to the operations field
            operations_str = self.json_serialize(payload)
            log.debug("operations %s", operations_str)
            data.add_field(
                "operations", operations_str, content_type="application/json"
            )

            # Add the file map field
            file_map_str = self.json_serialize(file_map)
            log.debug("file_map %s", file_map_str)
            data.add_field("map", file_map_str, content_type="application/json")

            # Add the extracted files as remaining fields
            for k, f in file_streams.items():
                name = getattr(f, "name", k)
                content_type = getattr(f, "content_type", None)

                data.add_field(k, f, filename=name, content_type=content_type)

            post_args: Dict[str, Any] = {"data": data}

        else:
            if variable_values:
                payload["variables"] = variable_values

            if log.isEnabledFor(logging.INFO):
                log.info(">>> %s", self.json_serialize(payload))

            post_args = {"json": payload}

        # Pass post_args to aiohttp post method
        if extra_args:
            post_args.update(extra_args)

        # Add headers for AppSync if requested
        if isinstance(self.auth, AppSyncAuthentication):
            post_args["headers"] = self.auth.get_headers(
                self.json_serialize(payload),
                {"content-type": "application/json"},
            )

        if self.session is None:
            raise TransportClosed("Transport is not connected")

        async with self.session.post(self.url, ssl=self.ssl, **post_args) as resp:

            # Saving latest response headers in the transport
            self.response_headers = resp.headers

            async def raise_response_error(resp: aiohttp.ClientResponse, reason: str):
                # We raise a TransportServerError if the status code is 400 or higher
                # We raise a TransportProtocolError in the other cases

                try:
                    # Raise a ClientResponseError if response status is 400 or higher
                    resp.raise_for_status()
                except ClientResponseError as e:
                    raise TransportServerError(str(e), e.status) from e

                result_text = await resp.text()
                raise TransportProtocolError(
                    f"Server did not return a GraphQL result: "
                    f"{reason}: "
                    f"{result_text}"
                )

            try:
                result = await resp.json(content_type=None)

                if log.isEnabledFor(logging.INFO):
                    result_text = await resp.text()
                    log.info("<<< %s", result_text)

            except Exception:
                await raise_response_error(resp, "Not a JSON answer")

            if result is None:
                await raise_response_error(resp, "Not a JSON answer")

            if "errors" not in result and "data" not in result:
                await raise_response_error(resp, 'No "data" or "errors" keys in answer')

            return ExecutionResult(
                errors=result.get("errors"),
                data=result.get("data"),
                extensions=result.get("extensions"),
            )

    def subscribe(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> AsyncGenerator[ExecutionResult, None]:
        """Subscribe is not supported on HTTP.

        :meta private:
        """
        raise NotImplementedError(" The HTTP transport does not support subscriptions")
