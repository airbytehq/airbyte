import io
import json
import logging
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

import httpx
from graphql import DocumentNode, ExecutionResult, print_ast

from ..utils import extract_files
from . import AsyncTransport, Transport
from .exceptions import (
    TransportAlreadyConnected,
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)

log = logging.getLogger(__name__)


class _HTTPXTransport:
    file_classes: Tuple[Type[Any], ...] = (io.IOBase,)

    response_headers: Optional[httpx.Headers] = None

    def __init__(
        self,
        url: Union[str, httpx.URL],
        json_serialize: Callable = json.dumps,
        **kwargs,
    ):
        """Initialize the transport with the given httpx parameters.

        :param url: The GraphQL server URL. Example: 'https://server.com:PORT/path'.
        :param json_serialize: Json serializer callable.
                By default json.dumps() function.
        :param kwargs: Extra args passed to the `httpx` client.
        """
        self.url = url
        self.json_serialize = json_serialize
        self.kwargs = kwargs

    def _prepare_request(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        extra_args: Optional[Dict[str, Any]] = None,
        upload_files: bool = False,
    ) -> Dict[str, Any]:
        query_str = print_ast(document)

        payload: Dict[str, Any] = {
            "query": query_str,
        }

        if operation_name:
            payload["operationName"] = operation_name

        if upload_files:
            # If the upload_files flag is set, then we need variable_values
            assert variable_values is not None

            post_args = self._prepare_file_uploads(variable_values, payload)
        else:
            if variable_values:
                payload["variables"] = variable_values

            post_args = {"json": payload}

        # Log the payload
        if log.isEnabledFor(logging.DEBUG):
            log.debug(">>> %s", self.json_serialize(payload))

        # Pass post_args to httpx post method
        if extra_args:
            post_args.update(extra_args)

        return post_args

    def _prepare_file_uploads(self, variable_values, payload) -> Dict[str, Any]:
        # If we upload files, we will extract the files present in the
        # variable_values dict and replace them by null values
        nulled_variable_values, files = extract_files(
            variables=variable_values,
            file_classes=self.file_classes,
        )

        # Save the nulled variable values in the payload
        payload["variables"] = nulled_variable_values

        # Prepare to send multipart-encoded data
        data: Dict[str, Any] = {}
        file_map: Dict[str, List[str]] = {}
        file_streams: Dict[str, Tuple[str, ...]] = {}

        for i, (path, f) in enumerate(files.items()):
            key = str(i)

            # Generate the file map
            # path is nested in a list because the spec allows multiple pointers
            # to the same file. But we don't support that.
            # Will generate something like {"0": ["variables.file"]}
            file_map[key] = [path]

            # Generate the file streams
            # Will generate something like
            # {"0": ("variables.file", <_io.BufferedReader ...>)}
            name = cast(str, getattr(f, "name", key))
            content_type = getattr(f, "content_type", None)

            if content_type is None:
                file_streams[key] = (name, f)
            else:
                file_streams[key] = (name, f, content_type)

        # Add the payload to the operations field
        operations_str = self.json_serialize(payload)
        log.debug("operations %s", operations_str)
        data["operations"] = operations_str

        # Add the file map field
        file_map_str = self.json_serialize(file_map)
        log.debug("file_map %s", file_map_str)
        data["map"] = file_map_str

        return {"data": data, "files": file_streams}

    def _prepare_result(self, response: httpx.Response) -> ExecutionResult:
        # Save latest response headers in transport
        self.response_headers = response.headers

        if log.isEnabledFor(logging.DEBUG):
            log.debug("<<< %s", response.text)

        try:
            result: Dict[str, Any] = response.json()

        except Exception:
            self._raise_response_error(response, "Not a JSON answer")

        if "errors" not in result and "data" not in result:
            self._raise_response_error(response, 'No "data" or "errors" keys in answer')

        return ExecutionResult(
            errors=result.get("errors"),
            data=result.get("data"),
            extensions=result.get("extensions"),
        )

    def _raise_response_error(self, response: httpx.Response, reason: str):
        # We raise a TransportServerError if the status code is 400 or higher
        # We raise a TransportProtocolError in the other cases

        try:
            # Raise a HTTPError if response status is 400 or higher
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise TransportServerError(str(e), e.response.status_code) from e

        raise TransportProtocolError(
            f"Server did not return a GraphQL result: " f"{reason}: " f"{response.text}"
        )


class HTTPXTransport(Transport, _HTTPXTransport):
    """:ref:`Sync Transport <sync_transports>` used to execute GraphQL queries
    on remote servers.

    The transport uses the httpx library to send HTTP POST requests.
    """

    client: Optional[httpx.Client] = None

    def connect(self):
        if self.client:
            raise TransportAlreadyConnected("Transport is already connected")

        log.debug("Connecting transport")

        self.client = httpx.Client(**self.kwargs)

    def execute(  # type: ignore
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        extra_args: Optional[Dict[str, Any]] = None,
        upload_files: bool = False,
    ) -> ExecutionResult:
        """Execute GraphQL query.

        Execute the provided document AST against the configured remote server. This
        uses the httpx library to perform a HTTP POST request to the remote server.

        :param document: GraphQL query as AST Node object.
        :param variable_values: Dictionary of input parameters (Default: None).
        :param operation_name: Name of the operation that shall be executed.
            Only required in multi-operation documents (Default: None).
        :param extra_args: additional arguments to send to the httpx post method
        :param upload_files: Set to True if you want to put files in the variable values
        :return: The result of execution.
            `data` is the result of executing the query, `errors` is null
            if no errors occurred, and is a non-empty array if an error occurred.
        """
        if not self.client:
            raise TransportClosed("Transport is not connected")

        post_args = self._prepare_request(
            document,
            variable_values,
            operation_name,
            extra_args,
            upload_files,
        )

        response = self.client.post(self.url, **post_args)

        return self._prepare_result(response)

    def close(self):
        """Closing the transport by closing the inner session"""
        if self.client:
            self.client.close()
            self.client = None


class HTTPXAsyncTransport(AsyncTransport, _HTTPXTransport):
    """:ref:`Async Transport <async_transports>` used to execute GraphQL queries
    on remote servers.

    The transport uses the httpx library with anyio.
    """

    client: Optional[httpx.AsyncClient] = None

    async def connect(self):
        if self.client:
            raise TransportAlreadyConnected("Transport is already connected")

        log.debug("Connecting transport")

        self.client = httpx.AsyncClient(**self.kwargs)

    async def execute(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        extra_args: Optional[Dict[str, Any]] = None,
        upload_files: bool = False,
    ) -> ExecutionResult:
        """Execute GraphQL query.

        Execute the provided document AST against the configured remote server. This
        uses the httpx library to perform a HTTP POST request asynchronously to the
        remote server.

        :param document: GraphQL query as AST Node object.
        :param variable_values: Dictionary of input parameters (Default: None).
        :param operation_name: Name of the operation that shall be executed.
            Only required in multi-operation documents (Default: None).
        :param extra_args: additional arguments to send to the httpx post method
        :param upload_files: Set to True if you want to put files in the variable values
        :return: The result of execution.
            `data` is the result of executing the query, `errors` is null
            if no errors occurred, and is a non-empty array if an error occurred.
        """
        if not self.client:
            raise TransportClosed("Transport is not connected")

        post_args = self._prepare_request(
            document,
            variable_values,
            operation_name,
            extra_args,
            upload_files,
        )

        response = await self.client.post(self.url, **post_args)

        return self._prepare_result(response)

    async def close(self):
        """Closing the transport by closing the inner session"""
        if self.client:
            await self.client.aclose()
            self.client = None

    def subscribe(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> AsyncGenerator[ExecutionResult, None]:
        """Subscribe is not supported on HTTP.

        :meta private:
        """
        raise NotImplementedError("The HTTP transport does not support subscriptions")
