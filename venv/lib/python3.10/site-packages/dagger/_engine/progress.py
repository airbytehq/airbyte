from dataclasses import dataclass, field

import anyio
from rich import get_console
from rich.console import Console
from rich.status import Status
from typing_extensions import Self

asyncify = anyio.to_thread.run_sync


@dataclass(slots=True)
class Progress:
    console: Console = field(default_factory=get_console)
    status: Status | None = field(default=None, init=False)

    async def start(self, status: str) -> None:
        self.status = Status(status, console=self.console)
        await asyncify(self.status.start)

    async def stop(self) -> None:
        if self.status:
            await asyncify(self.status.stop)
            self.status = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:
        await self.stop()

    async def update(self, message: str) -> None:
        if self.status:
            await asyncify(self.status.update, message)

    def update_sync(self, message: str) -> None:
        if self.status:
            self.status.update(message)
