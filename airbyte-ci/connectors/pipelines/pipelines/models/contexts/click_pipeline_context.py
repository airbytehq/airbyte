#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TextIO, Tuple

import anyio
import dagger
from asyncclick import Context, get_current_context
from pipelines import main_logger
from pipelines.cli.click_decorators import LazyPassDecorator
from pydantic import BaseModel, Field, PrivateAttr

from ..singleton import Singleton


class ClickPipelineContext(BaseModel, Singleton):
    """
    A replacement class for the Click context object passed to click functions.

    This class is meant to serve as a singleton object that initializes and holds onto a single instance of the
    Dagger client, which is used to create containers for running pipelines.
    """

    dockerd_service: Optional[dagger.Container] = Field(default=None)
    _dagger_client: Optional[dagger.Client] = PrivateAttr(default=None)
    _click_context: Callable[[], Context] = PrivateAttr(default_factory=lambda: get_current_context)
    _og_click_context: Context = PrivateAttr(default=None)

    @property
    def params(self) -> Dict[str, Any]:
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

    def __init__(self, **data: dict[str, Any]) -> None:
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

    async def get_dagger_client(self, pipeline_name: Optional[str] = None) -> dagger.Client:
        """
        Get (or initialize) the Dagger Client instance.
        """
        if not self._dagger_client:
            async with self._dagger_client_lock:
                if not self._dagger_client:

                    connection = dagger.Connection(dagger.Config(log_output=self.get_log_output()))
                    """
                    Sets up the '_dagger_client' attribute, intended for single-threaded use within connectors.

                    Caution:
                        Avoid using this client across multiple thread pools, as it can lead to errors.
                        Cross-thread pool calls are generally considered an anti-pattern.
                    """
                    self._dagger_client = await self._og_click_context.with_async_resource(connection)

        assert self._dagger_client, "Error initializing Dagger client"
        return self._dagger_client.pipeline(pipeline_name) if pipeline_name else self._dagger_client

    def get_log_output(self) -> TextIO:
        # This `show_dagger_logs` flag is likely going to be removed in the future.
        # See https://github.com/airbytehq/airbyte/issues/33487
        if self.params.get("show_dagger_logs", False):
            return sys.stdout
        else:
            log_output, self._click_context().obj["dagger_logs_path"] = self._create_dagger_client_log_file()
            return log_output

    def _create_dagger_client_log_file(self) -> Tuple[TextIO, Path]:
        """
        Create the dagger client log file.
        """
        dagger_logs_file_descriptor, dagger_logs_temp_file_path = tempfile.mkstemp(dir="/tmp", prefix="dagger_client_", suffix=".log")
        main_logger.info(f"Dagger client logs stored in {dagger_logs_temp_file_path}")
        return io.TextIOWrapper(io.FileIO(dagger_logs_file_descriptor, "w+")), Path(dagger_logs_temp_file_path)


# Create @pass_pipeline_context decorator for use in click commands
pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)
