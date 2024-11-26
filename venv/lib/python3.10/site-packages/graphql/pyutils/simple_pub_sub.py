from asyncio import Future, Queue, ensure_future, sleep
from inspect import isawaitable
from typing import Any, AsyncIterator, Callable, Optional, Set

try:
    from asyncio import get_running_loop
except ImportError:
    from asyncio import get_event_loop as get_running_loop  # Python < 3.7


__all__ = ["SimplePubSub", "SimplePubSubIterator"]


class SimplePubSub:
    """A very simple publish-subscript system.

    Creates an AsyncIterator from an EventEmitter.

    Useful for mocking a PubSub system for tests.
    """

    subscribers: Set[Callable]

    def __init__(self) -> None:
        self.subscribers = set()

    def emit(self, event: Any) -> bool:
        """Emit an event."""
        for subscriber in self.subscribers:
            result = subscriber(event)
            if isawaitable(result):
                ensure_future(result)
        return bool(self.subscribers)

    def get_subscriber(
        self, transform: Optional[Callable] = None
    ) -> "SimplePubSubIterator":
        return SimplePubSubIterator(self, transform)


class SimplePubSubIterator(AsyncIterator):
    def __init__(self, pubsub: SimplePubSub, transform: Optional[Callable]) -> None:
        self.pubsub = pubsub
        self.transform = transform
        self.pull_queue: Queue[Future] = Queue()
        self.push_queue: Queue[Any] = Queue()
        self.listening = True
        pubsub.subscribers.add(self.push_value)

    def __aiter__(self) -> "SimplePubSubIterator":
        return self

    async def __anext__(self) -> Any:
        if not self.listening:
            raise StopAsyncIteration
        await sleep(0)
        if not self.push_queue.empty():
            return await self.push_queue.get()
        future = get_running_loop().create_future()
        await self.pull_queue.put(future)
        return future

    async def aclose(self) -> None:
        if self.listening:
            await self.empty_queue()

    async def empty_queue(self) -> None:
        self.listening = False
        self.pubsub.subscribers.remove(self.push_value)
        while not self.pull_queue.empty():
            future = await self.pull_queue.get()
            future.cancel()
        while not self.push_queue.empty():
            await self.push_queue.get()

    async def push_value(self, event: Any) -> None:
        value = event if self.transform is None else self.transform(event)
        if self.pull_queue.empty():
            await self.push_queue.put(value)
        else:
            (await self.pull_queue.get()).set_result(value)
