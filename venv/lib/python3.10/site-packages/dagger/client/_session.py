import contextlib
import logging
import os
from dataclasses import dataclass, field
from typing import Any

import graphql
import httpx
from gql.client import AsyncClientSession
from gql.client import Client as GraphQLClient
from gql.transport.exceptions import (
    TransportProtocolError,
    TransportQueryError,
    TransportServerError,
)
from typing_extensions import Self

from dagger import ClientConnectionError
from dagger._config import ConnectConfig, Retry
from dagger._managers import ResourceManager

from ._transport.httpx import HTTPXAsyncTransport

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class ConnectParams:
    """Options for making a session connection. For internal use only."""

    port: int
    session_token: str
    url: httpx.URL = field(init=False)

    def __post_init__(self):
        self.port = int(self.port)
        if self.port < 1:
            msg = f"Invalid port value: {self.port}"
            raise ValueError(msg)
        self.url = httpx.URL(f"http://127.0.0.1:{self.port}/query")

    @classmethod
    def from_env(cls) -> "ConnectParams | None":
        if not (port := os.getenv("DAGGER_SESSION_PORT")):
            return None
        if not (token := os.getenv("DAGGER_SESSION_TOKEN")):
            msg = "DAGGER_SESSION_TOKEN must be set when using DAGGER_SESSION_PORT"
            raise ClientConnectionError(msg)
        try:
            return cls(port=int(port), session_token=token)
        except ValueError as e:
            # only port is validated
            msg = f"Invalid DAGGER_SESSION_PORT: {port}"
            raise ClientConnectionError(msg) from e


class ClientSession(ResourceManager):
    """Establish a GraphQL client connection to the engine."""

    def __init__(self, conn: ConnectParams, cfg: ConnectConfig | None = None):
        super().__init__()

        if cfg is None:
            cfg = ConnectConfig()

        transport = HTTPXAsyncTransport(
            conn.url,
            timeout=cfg.timeout,
            auth=(conn.session_token, ""),
        )

        client = GraphQLClient(
            transport=transport,
            fetch_schema_from_transport=True,
            # We're using the timeout from the httpx transport.
            execute_timeout=None,
        )

        self.client = retrying_client(client, cfg.retry) if cfg.retry else client
        self._session: AsyncClientSession | None = None

    async def start(self) -> AsyncClientSession:
        if self._session:
            return self._session

        async with self.get_stack() as stack:
            logger.debug("Establishing client session to GraphQL server")
            try:
                session = await stack.enter_async_context(self.client)
            except TimeoutError as e:
                msg = f"Failed to connect to engine: {e}"
                raise ClientConnectionError(msg) from e
            except httpx.RequestError as e:
                msg = f"Could not make request: {e}"
                raise ClientConnectionError(msg) from e
            except (TransportProtocolError, TransportServerError) as e:
                msg = f"Got unexpected response from engine: {e}"
                raise ClientConnectionError(msg) from e
            except TransportQueryError as e:
                # Only query during connection is the introspection query
                # for building the schema.
                msg = str(e)
                # Extract only the error message.
                if e.errors and "message" in e.errors[0]:
                    msg = e.errors[0]["message"].strip()
                msg = f"Failed to build schema from introspection query: {msg}"
                raise ClientConnectionError(msg) from e

            self._session = session
            return session

    def has_session(self):
        return self._session is not None

    async def get_session(self) -> AsyncClientSession:
        return await self.start()

    async def get_schema(self) -> graphql.GraphQLSchema:
        client = (await self.get_session()).client
        if not client.schema:
            msg = "No schema in session"
            raise ClientConnectionError(msg)
        return client.schema

    async def execute(self, query: graphql.DocumentNode) -> Any:
        return await (await self.get_session()).execute(query)

    async def close(self) -> None:
        logger.debug("Closing client session to GraphQL server")
        await super().close()


@contextlib.asynccontextmanager
async def retrying_client(client: GraphQLClient, retry: Retry):
    try:
        yield await client.connect_async(
            reconnecting=True,
            retry_connect=retry.connect,
            retry_execute=retry.execute,
        )
    finally:
        await client.close_async()


class BaseConnection:
    session: ClientSession

    async def connect(self) -> Self:
        await self.session.start()
        return self

    async def close(self) -> None:
        await self.session.close()

    async def aclose(self) -> None:
        await self.close()

    def __await__(self):
        return self.connect().__await__()

    async def __aenter__(self) -> Self:
        return await self.connect()

    async def __aexit__(self, *_) -> None:
        await self.close()


class SingleConnection(BaseConnection):
    """Establish a GraphQL client connection to the Dagger API server."""

    def __init__(self, conn: ConnectParams, cfg: ConnectConfig | None = None):
        self.session = ClientSession(conn, cfg)


class SharedConnection(BaseConnection):
    """Establish a GraphQL client connection to the Dagger API server.

    Uses a lazy and shared connection.
    """

    _instance: Self | None = None
    _session: ClientSession | None = None
    _params: ConnectParams | None = None
    _cfg: ConnectConfig

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._cfg = ConnectConfig()
        return cls._instance

    def __init__(self) -> None:
        # This is a singleton class, so we don't want to initialize.
        ...

    def with_params(self, params: ConnectParams) -> Self:
        """Set the connection params."""
        if self._session:
            logger.warning(
                "Cannot set connection params after connection already started"
            )
        else:
            self._params = params
        return self

    def with_config(self, cfg: ConnectConfig) -> Self:
        """Set the connection config."""
        if self._session:
            logger.warning(
                "Cannot set connection config after connection already started"
            )
        else:
            self._cfg = cfg
        return self

    @property
    def session(self) -> ClientSession:
        if not self._session:
            logger.debug("Configuring shared connection to GraphQL server")

            # Delay checking the environment until we actually need it.
            if not self._params:
                self._params = ConnectParams.from_env()

            if not self._params:
                msg = "No active engine session to connect to"
                raise ClientConnectionError(msg)

            self._session = ClientSession(self._params, self._cfg)
        return self._session

    def is_connected(self) -> bool:
        return self._session is not None and self._session.has_session()

    async def close(self) -> None:
        if self._session:
            await super().close()
            self._session = None
