import contextlib
import logging

from dagger import Config

from ._engine.conn import Engine, provision_engine
from ._managers import ResourceManager
from .client._session import SharedConnection

logger = logging.getLogger(__name__)


class Connection(ResourceManager):
    """Connect to a Dagger Engine with an isolated client (legacy).

    This is an older version of :py:func:`dagger.connection` that uses an isolated
    client instance. Should no longer be used in newer projects unless there's
    a specific reason to do so.

    Example::

        import dagger

        async def main():
            async with dagger.Connection() as client:
                ctr = client.container().from_("alpine")


    You can stream the logs from the engine to see progress::

        import sys
        import anyio
        import dagger

        async def main():
            cfg = dagger.Config(log_output=sys.stderr)

            async with dagger.Connection(cfg) as client:
                ctr = client.container().from_("python:3.11.1-alpine")
                version = await ctr.with_exec(["python", "-V"]).stdout()

            print(version)
            # Output: Python 3.11.1

        anyio.run(main)
    """

    def __init__(self, config: Config | None = None) -> None:
        super().__init__()
        self.cfg = config or Config()

    async def __aenter__(self):
        logger.debug("Establishing connection with isolated client")
        async with self.get_stack() as stack:
            engine = await Engine(self.cfg, stack).provision()
            conn = engine.get_client_connection()
            return await engine.setup_client(conn)

    async def close(self):
        logger.debug("Closing connection with isolated client")
        await super().close()


@contextlib.asynccontextmanager
async def connection(config: Config | None = None):
    """Connect to a Dagger Engine using the global client.

    This is similar to :py:class:`dagger.Connection` but uses a global client
    (:py:attr:`dagger.dag`) so there's no need to pass around a client instance
    with this.

    Example::

        import dagger
        from dagger import dag

        async def main():
            async with dagger.connection():
                ctr = dag.container().from_("alpine")

            # Connection is closed when leaving the context manager's scope.


    You can stream the logs from the engine to see progress::

        import sys
        import anyio
        import dagger
        from dagger import dag

        async def main():
            cfg = dagger.Config(log_output=sys.stderr)

            async with dagger.connection(cfg):
                ctr = dag.container().from_("python:3.11.1-alpine")
                version = await ctr.with_exec(["python", "-V"]).stdout()

            print(version)
            # Output: Python 3.11.1

        anyio.run(main)
    """
    logger.debug("Establishing connection with shared client")
    async with provision_engine(config or Config()) as engine:
        conn = engine.get_shared_client_connection()
        await engine.setup_client(conn)
        yield conn
        logger.debug("Closing connection with shared client")


_shared = SharedConnection()
connect = _shared.connect
close = _shared.close
