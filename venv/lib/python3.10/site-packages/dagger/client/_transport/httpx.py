# flake8: noqa
"""
GraphQL client transport using HTTPX.

TODO: remove this file when gql releases a version with httpx support.
    It was added in https://github.com/graphql-python/gql/pull/370
"""
import io
import json
import logging
from typing import Any, AsyncGenerator, Callable, Dict, Optional, Tuple, Type, Union

import httpx
from gql.transport import AsyncTransport, Transport
from gql.transport.exceptions import (
    TransportAlreadyConnected,
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)
from graphql import DocumentNode, ExecutionResult, print_ast

log = logging.getLogger(__name__)


class _HTTPXTransport:
    file_classes: Tuple[Type[Any], ...] = (io.IOBase,)

    reponse_headers: Optional[httpx.Headers] = None

    def __init__(
        self,
        url: Union[str, httpx.URL],
        json_serialize: Callable = json.dumps,
        **kwargs,
    ):
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

        if variable_values:
            payload["variables"] = variable_values

        post_args = {"json": payload}

        # Log the payload
        if log.isEnabledFor(logging.DEBUG):
            log.debug(">>> %s", self.json_serialize(payload))

        # Pass post_args to httpx post method
        if extra_args:
            post_args |= extra_args

        return post_args

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
            f"Server did not return a GraphQL result: {reason}: {response.text}"
        )


class HTTPXTransport(Transport, _HTTPXTransport):
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
        if self.client:
            self.client.close()
            self.client = None


class HTTPXAsyncTransport(AsyncTransport, _HTTPXTransport):
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
        if not self.client:
            raise TransportClosed("Transport is not connected")

        post_args = self._prepare_request(
            document,
            variable_values,
            operation_name,
            extra_args,
        )

        response = await self.client.post(self.url, **post_args)

        return self._prepare_result(response)

    async def close(self):
        """Closing the transport by closing the inner session."""
        if self.client:
            await self.client.aclose()
            self.client = None

    def subscribe(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> AsyncGenerator[ExecutionResult, None]:
        raise NotImplementedError("The HTTP transport does not support subscriptions")
