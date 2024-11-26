import contextlib
import typing

import anyio.to_thread
from typing_extensions import Self

asyncify = anyio.to_thread.run_sync


class ResourceManager(contextlib.AbstractAsyncContextManager):
    def __init__(self):
        super().__init__()
        self.stack = contextlib.AsyncExitStack()

    @contextlib.asynccontextmanager
    async def get_stack(self) -> typing.AsyncIterator[contextlib.AsyncExitStack]:
        async with self.stack as stack:
            yield stack
            self.stack = stack.pop_all()

    # For type checker as inherited method isn't typed.
    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()

    async def start(self) -> None:
        ...

    async def close(self) -> None:
        await self.stack.aclose()

    # For compatibility with contextlib.aclosing.
    async def aclose(self) -> None:
        await self.close()


T = typing.TypeVar("T")


class SyncResource(contextlib.AbstractAsyncContextManager[T], typing.Generic[T]):
    """Wrap a blocking sync context manager in a non-blocking async context manager."""

    def __init__(self, cm: typing.ContextManager[T]):
        self.sync_cm = cm

    async def __aenter__(self) -> T:
        return await asyncify(self.sync_cm.__enter__)

    async def __aexit__(self, *exc_details) -> None:
        await asyncify(self.sync_cm.__exit__, *exc_details)
