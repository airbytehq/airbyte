#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
from typing import Any, Callable, Optional

import anyio
import dagger
from asyncclick import Context, get_current_context
from dagger.api.gen import Client, Container
from pipelines.cli.click_decorators import LazyPassDecorator
from pydantic import BaseModel, Field, PrivateAttr

from ..singleton import Singleton


class ClickPipelineContext(BaseModel, Singleton):
    """
    A replacement class for the Click context object passed to click functions.

    This class is meant to serve as a singleton object that initializes and holds onto a single instance of the
    Dagger client, which is used to create containers for running pipelines.
    """

    dockerd_service: Optional[Container] = Field(default=None)
    _dagger_client: Optional[Client] = PrivateAttr(default=None)
    _click_context: Callable[[], Context] = PrivateAttr(default_factory=lambda: get_current_context)
    _og_click_context: Callable[[], Context] = PrivateAttr(default=None)

    @property
    def params(self):
        """
        Returns a combination of the click context object and the click context params.

        This means that any arguments or options defined in the parent command will be available to the child command.
        """
        ctx = self._click_context()
        click_obj = ctx.obj
        click_params = ctx.params
        command_name = ctx.command.name

        # Error if click_obj and click_params have the same key, and not the same value
        intersection = set(click_obj.keys()) & set(click_params.keys())
        if intersection:
            for key in intersection:
                if click_obj[key] != click_params[key]:
                    raise ValueError(
                        f"Your command '{command_name}' has defined options/arguments with the same key as its parent, but with different values: {intersection}"
                    )

        return {**click_obj, **click_params}

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: dict[str, Any]):
        """
        Initialize the ClickPipelineContext instance.

        This method checks the _initialized flag for the ClickPipelineContext class in the Singleton base class.
        If the flag is False, the initialization logic is executed and the flag is set to True.
        If the flag is True, the initialization logic is skipped.

        This ensures that the initialization logic is only executed once, even if the ClickPipelineContext instance is retrieved multiple times.
        This can be useful if the initialization logic is expensive (e.g., it involves network requests or database queries).
        """
        if not Singleton._initialized[ClickPipelineContext]:
            super().__init__(**data)
            Singleton._initialized[ClickPipelineContext] = True

            """
            Note: Its important to hold onto the original click context object, as it is used to hold onto the Dagger client.
            """
            self._og_click_context = self._click_context()

    _dagger_client_lock: anyio.Lock = PrivateAttr(default_factory=anyio.Lock)

    async def get_dagger_client(self, pipeline_name: Optional[str] = None) -> Client:
        """
        Get (or initialize) the Dagger Client instance.
        """
        if not self._dagger_client:
            async with self._dagger_client_lock:
                if not self._dagger_client:
                    connection = dagger.Connection(dagger.Config(log_output=sys.stdout))

                    """
                    Sets up the '_dagger_client' attribute, intended for single-threaded use within connectors.

                    Caution:
                        Avoid using this client across multiple thread pools, as it can lead to errors.
                        Cross-thread pool calls are generally considered an anti-pattern.
                    """
                    self._dagger_client = await self._og_click_context.with_async_resource(connection)  # type: ignore

        assert self._dagger_client, "Error initializing Dagger client"
        return self._dagger_client.pipeline(pipeline_name) if pipeline_name else self._dagger_client


# Create @pass_pipeline_context decorator for use in click commands
pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)
