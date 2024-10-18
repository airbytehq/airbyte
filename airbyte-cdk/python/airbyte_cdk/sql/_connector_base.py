# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Destination base classes."""

from __future__ import annotations

import abc
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

import jsonschema
import rich
import yaml
from rich.syntax import Syntax

from airbyte_cdk.models import (
    AirbyteMessage,
    ConnectorSpecification,
    Status,
    TraceType,
    Type,
)

from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._util.connector_info import ConnectorRuntimeInfo
from airbyte_cdk.sql._util.hashing import one_way_hash
from airbyte_cdk.sql._util.telemetry import (
    EventState,
    log_config_validation_result,
    log_connector_check_result,
)
from airbyte_cdk.sql._util.temp_files import as_temp_files
from airbyte_cdk.sql.logs import new_passthrough_file_logger


if TYPE_CHECKING:
    import logging
    from collections.abc import Generator
    from typing import IO

    from airbyte_cdk.sql._executors.base import Executor
    from airbyte_cdk.sql._message_iterators import AirbyteMessageIterator
    from airbyte_cdk.sql.progress import ProgressTracker


MAX_LOG_LINES = 20


class ConnectorBase(abc.ABC):
    """A class representing a destination that can be called."""

    connector_type: Literal["destination", "source"]

    def __init__(
        self,
        executor: Executor,
        name: str,
        config: dict[str, Any] | None = None,
        *,
        validate: bool = False,
    ) -> None:
        """Initialize the source.

        If config is provided, it will be validated against the spec if validate is True.
        """
        self.executor = executor
        self._name = name
        self._config_dict: dict[str, Any] | None = None
        self._last_log_messages: list[str] = []
        self._spec: ConnectorSpecification | None = None
        self._selected_stream_names: list[str] = []
        self._file_logger: logging.Logger = new_passthrough_file_logger(self._name)
        if config is not None:
            self.set_config(config, validate=validate)

    @property
    def name(self) -> str:
        """Get the name of the connector."""
        return self._name

    def _get_connector_runtime_info(self) -> ConnectorRuntimeInfo:
        """Get metadata for telemetry and performance logging."""
        return ConnectorRuntimeInfo(
            name=self.name,
            version=self.connector_version,
            executor_type=type(self.executor).__name__,
            config_hash=self.config_hash,
        )

    def _print_info_message(
        self,
        message: str,
    ) -> None:
        """Print a message to the logger."""
        if self._file_logger:
            self._file_logger.info(message)

    def _print_error_message(
        self,
        message: str,
    ) -> None:
        """Print a message to the console and the logger."""
        rich.print(f"ERROR: {message}")
        if self._file_logger:
            self._file_logger.error(message)

    def set_config(
        self,
        config: dict[str, Any],
        *,
        validate: bool = True,
    ) -> None:
        """Set the config for the connector.

        If validate is True, raise an exception if the config fails validation.

        If validate is False, validation will be deferred until check() or validate_config()
        is called.
        """
        if validate:
            self.validate_config(config)

        self._config_dict = config

    def get_config(self) -> dict[str, Any]:
        """Get the config for the connector."""
        return self._config

    @property
    def _config(self) -> dict[str, Any]:
        if self._config_dict is None:
            raise exc.AirbyteConnectorConfigurationMissingError(
                connector_name=self.name,
                guidance="Provide via get_destination() or set_config()",
            )
        return self._config_dict

    @property
    def config_hash(self) -> str | None:
        """Get a hash of the current config.

        Returns None if the config is not set.
        """
        if self._config_dict is None:
            return None

        try:
            return one_way_hash(self._config_dict)
        except Exception:
            # This can fail if there are unhashable values in the config,
            # or unexpected data types. In this case, return None.
            return None

    def validate_config(self, config: dict[str, Any] | None = None) -> None:
        """Validate the config against the spec.

        If config is not provided, the already-set config will be validated.
        """
        spec = self._get_spec(force_refresh=False)
        config = self._config if config is None else config
        try:
            jsonschema.validate(config, spec.connectionSpecification)
            log_config_validation_result(
                name=self.name,
                state=EventState.SUCCEEDED,
            )
        except jsonschema.ValidationError as ex:
            validation_ex = exc.AirbyteConnectorValidationFailedError(
                connector_name=self.name,
                message="The provided config is not valid.",
                context={
                    "error_message": ex.message,
                    "error_path": ex.path,
                    "error_instance": ex.instance,
                    "error_schema": ex.schema,
                },
            )
            log_config_validation_result(
                name=self.name,
                state=EventState.FAILED,
                exception=validation_ex,
            )
            raise validation_ex from ex

    def _get_spec(self, *, force_refresh: bool = False) -> ConnectorSpecification:
        """Call spec on the connector.

        This involves the following steps:
        * execute the connector with spec
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.

        Raises:
            AirbyteConnectorSpecFailedError: If the spec operation fails.
            AirbyteConnectorMissingSpecError: If the spec operation does not return a spec.
        """
        if force_refresh or self._spec is None:
            try:
                for msg in self._execute(["spec"]):
                    if msg.type == Type.SPEC and msg.spec:
                        self._spec = msg.spec
                        break

            except exc.AirbyteSubprocessError as ex:
                raise exc.AirbyteConnectorSpecFailedError(
                    connector_name=self.name,
                    log_text=ex.log_text,
                ) from ex

        if self._spec:
            return self._spec

        raise exc.AirbyteConnectorMissingSpecError(
            connector_name=self.name,
            log_text=self._last_log_messages,
        )

    @property
    def config_spec(self) -> dict[str, Any]:
        """Generate a configuration spec for this connector, as a JSON Schema definition.

        This function generates a JSON Schema dictionary with configuration specs for the
        current connector, as a dictionary.

        Returns:
            dict: The JSON Schema configuration spec as a dictionary.
        """
        return cast(dict[str, Any], self._get_spec(force_refresh=True).connectionSpecification)

    def print_config_spec(
        self,
        format: Literal["yaml", "json"] = "yaml",  # noqa: A002
        *,
        output_file: Path | str | None = None,
    ) -> None:
        """Print the configuration spec for this connector.

        Args:
            format: The format to print the spec in. Must be "yaml" or "json".
            output_file: Optional. If set, the spec will be written to the given file path.
                Otherwise, it will be printed to the console.
        """
        if format not in {"yaml", "json"}:
            raise exc.AirbyteInputError(
                message="Invalid format. Expected 'yaml' or 'json'",
                input_value=format,
            )
        if isinstance(output_file, str):
            output_file = Path(output_file)

        if format == "yaml":
            content = yaml.dump(self.config_spec, indent=2)
        elif format == "json":
            content = json.dumps(self.config_spec, indent=2)

        if output_file:
            output_file.write_text(content)
            return

        syntax_highlighted = Syntax(content, format)
        rich.print(syntax_highlighted)

    @property
    def _yaml_spec(self) -> str:
        """Get the spec as a yaml string.

        For now, the primary use case is for writing and debugging a valid config for a source.

        This is private for now because we probably want better polish before exposing this
        as a stable interface. This will also get easier when we have docs links with this info
        for each connector.
        """
        spec_obj: ConnectorSpecification = self._get_spec()
        spec_dict = spec_obj.dict(exclude_unset=True)
        # convert to a yaml string
        return yaml.dump(spec_dict)

    @property
    def docs_url(self) -> str:
        """Get the URL to the connector's documentation."""
        return f"https://docs.airbyte.com/integrations/{self.connector_type}s/" + self.name.lower().replace(f"{self.connector_type}-", "")

    @property
    def connector_version(self) -> str | None:
        """Return the version of the connector as reported by the executor.

        Returns None if the version cannot be determined.
        """
        try:
            return self.executor.get_installed_version()
        except Exception:
            # Version not detected, so return None.
            return None

    def check(self) -> None:
        """Call check on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with check --config <config_file>
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        with as_temp_files([self._config]) as [config_file]:
            try:
                for msg in self._execute(["check", "--config", config_file]):
                    if msg.type == Type.CONNECTION_STATUS and msg.connectionStatus:
                        if msg.connectionStatus.status != Status.FAILED:
                            rich.print(f"Connection check succeeded for `{self.name}`.")
                            log_connector_check_result(
                                name=self.name,
                                state=EventState.SUCCEEDED,
                            )
                            return

                        log_connector_check_result(
                            name=self.name,
                            state=EventState.FAILED,
                        )
                        raise exc.AirbyteConnectorCheckFailedError(
                            connector_name=self.name,
                            help_url=self.docs_url,
                            context={
                                "failure_reason": msg.connectionStatus.message,
                            },
                        )
                raise exc.AirbyteConnectorCheckFailedError(
                    connector_name=self.name,
                    message="The connector `check` operation did not return a status.",
                    log_text=self._last_log_messages,
                )
            except exc.AirbyteConnectorFailedError as ex:
                raise exc.AirbyteConnectorCheckFailedError(
                    connector_name=self.name,
                    original_exception=ex,
                ) from None

    def install(self) -> None:
        """Install the connector if it is not yet installed."""
        self.executor.install()
        rich.print("For configuration instructions, see: \n" f"{self.docs_url}#reference\n")

    def uninstall(self) -> None:
        """Uninstall the connector if it is installed.

        This only works if the use_local_install flag wasn't used and installation is managed by
        Airbyte.
        """
        self.executor.uninstall()

    def _peek_airbyte_message(
        self,
        message: AirbyteMessage,
        *,
        raise_on_error: bool = True,
    ) -> None:
        """Process an Airbyte message.

        This method handles reading Airbyte messages and taking action, if needed, based on the
        message type. For instance, log messages are logged, records are tallied, and errors are
        raised as exceptions if `raise_on_error` is True.

        Raises:
            AirbyteConnectorFailedError: If a TRACE message of type ERROR is emitted.
        """
        if message.type == Type.LOG and message.log is not None:
            self._print_info_message(message.log.message)
            return

        if message.type == Type.TRACE and message.trace is not None and message.trace.type == TraceType.ERROR:
            self._print_error_message(message.trace.error.message)
            if raise_on_error:
                raise exc.AirbyteConnectorFailedError(
                    connector_name=self.name,
                    message=message.trace.error.message,
                    log_text=self._last_log_messages,
                )
            return

    def _execute(
        self,
        args: list[str],
        stdin: IO[str] | AirbyteMessageIterator | None = None,
        *,
        progress_tracker: ProgressTracker | None = None,
    ) -> Generator[AirbyteMessage, None, None]:
        """Execute the connector with the given arguments.

        This involves the following steps:
        * Locate the right venv. It is called ".venv-<connector_name>"
        * Spawn a subprocess with .venv-<connector_name>/bin/<connector-name> <args>
        * Read the output line by line of the subprocess and serialize them AirbyteMessage objects.
          Drop if not valid.

        Raises:
            AirbyteConnectorFailedError: If the process returns a failure status (non-zero).
        """
        # Fail early if the connector is not installed.
        self.executor.ensure_installation(auto_fix=False)

        # When calculating MB read, we need to account for the envelope size.
        # Note our priority is to keep performance up, while providing at least rough
        # alignment with comparable metrics in Airbyte Cloud.
        envelope_size = len(
            json.dumps(
                {
                    "type": "RECORD",
                    "record": {
                        "stream": "",
                        "data": {},
                        "emitted_at": 1234567890,
                        # "namespace": "",  # We're knowingly omitting this to keep perf impact low.
                    },
                }
            )
        )

        try:
            for line in self.executor.execute(args, stdin=stdin):
                try:
                    message: AirbyteMessage = AirbyteMessage(json.loads(line))
                    if progress_tracker and message.record:
                        stream_name = message.record.stream
                        progress_tracker.tally_bytes_read(
                            bytes_read=len(line) - envelope_size - len(stream_name),
                            stream_name=stream_name,
                        )
                    self._peek_airbyte_message(message)
                    yield message

                except Exception:
                    # This is likely a log message, so log it as INFO.
                    self._print_info_message(line)

        except exc.AirbyteSubprocessFailedError as ex:
            # Generic subprocess failure, so raise a connector error.
            raise exc.AirbyteConnectorFailedError(
                connector_name=self.name,
                log_text=ex.log_text,
                context={
                    "exit_code": ex.exit_code,
                },
            ) from None
        except Exception as e:
            # This is an unexpected error, so wrap the original exception when raising.
            raise exc.AirbyteConnectorFailedError(
                connector_name=self.name,
                log_text=self._last_log_messages,
                original_exception=e,
            ) from None


__all__ = [
    "ConnectorBase",
]
