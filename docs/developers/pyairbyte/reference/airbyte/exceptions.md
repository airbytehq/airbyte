---
id: airbyte-exceptions
title: airbyte.exceptions
---

Module airbyte.exceptions
=========================
All exceptions used in the PyAirbyte.

This design is modeled after structlog's exceptions, in that we bias towards auto-generated
property prints rather than sentence-like string concatenation.

E.g. Instead of this:

> `Subprocess failed with exit code '1'`

We do this:

> `Subprocess failed. (exit_code=1)`

The benefit of this approach is that we can easily support structured logging, and we can
easily add new properties to exceptions without having to update all the places where they
are raised. We can also support any arbitrary number of properties in exceptions, without spending
time on building sentence-like string constructions with optional inputs.

In addition, the following principles are applied for exception class design:

- All exceptions inherit from a common base class.
- All exceptions have a message attribute.
- The first line of the docstring is used as the default message.
- The default message can be overridden by explicitly setting the message attribute.
- Exceptions may optionally have a guidance attribute.
- Exceptions may optionally have a help_url attribute.
- Rendering is automatically handled by the base class.
- Any helpful context not defined by the exception class can be passed in the `context` dict arg.
- Within reason, avoid sending PII to the exception constructor.
- Exceptions are dataclasses, so they can be instantiated with keyword arguments.
- Use the 'from' syntax to chain exceptions when it is helpful to do so.
  E.g. `raise AirbyteConnectorNotFoundError(...) from FileNotFoundError(connector_path)`
- Any exception that adds a new property should also be decorated as `@dataclass`.

Classes
-------

`AirbyteConnectionError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None, connection_id: str | None = None, job_id: int | None = None, job_status: str | None = None)`
:   An connection error occurred while communicating with the hosted Airbyte instance.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteConnectionSyncError

    ### Instance variables

    `connection_id: str | None`
    :   The connection ID where the error occurred.

    `connection_url: str | None`
    :   The web URL to the connection where the error occurred.

    `job_history_url: str | None`
    :   The URL to the job history where the error occurred.

    `job_id: int | None`
    :   The job ID where the error occurred (if applicable).

    `job_status: str | None`
    :   The latest status of the job where the error occurred (if applicable).

    `job_url: str | None`
    :   The URL to the job where the error occurred.

`AirbyteConnectionSyncError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None, connection_id: str | None = None, job_id: int | None = None, job_status: str | None = None)`
:   An error occurred while executing the remote Airbyte job.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectionError
    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteConnectionSyncTimeoutError

`AirbyteConnectionSyncTimeoutError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None, connection_id: str | None = None, job_id: int | None = None, job_status: str | None = None, timeout: int | None = None)`
:   An timeout occurred while waiting for the remote Airbyte job to complete.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectionSyncError
    * airbyte.exceptions.AirbyteConnectionError
    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `timeout: int | None`
    :   The timeout in seconds that was reached.

`AirbyteConnectorCheckFailedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector check failed.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

`AirbyteConnectorConfigurationMissingError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector is missing configuration.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteCacheError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `connector_name: str | None`
    :

`AirbyteConnectorDiscoverFailedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Error when running discovery on the connector.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteConnectorError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Error when running the connector.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteConnectorCheckFailedError
    * airbyte.exceptions.AirbyteConnectorDiscoverFailedError
    * airbyte.exceptions.AirbyteConnectorExecutableNotFoundError
    * airbyte.exceptions.AirbyteConnectorFailedError
    * airbyte.exceptions.AirbyteConnectorInstallationError
    * airbyte.exceptions.AirbyteConnectorMissingCatalogError
    * airbyte.exceptions.AirbyteConnectorMissingSpecError
    * airbyte.exceptions.AirbyteConnectorReadError
    * airbyte.exceptions.AirbyteConnectorSpecFailedError
    * airbyte.exceptions.AirbyteConnectorValidationFailedError
    * airbyte.exceptions.AirbyteConnectorWriteError
    * airbyte.exceptions.AirbyteNoDataFromConnectorError
    * airbyte.exceptions.AirbyteStateNotFoundError
    * airbyte.exceptions.AirbyteStreamNotFoundError

    ### Instance variables

    `connector_name: str | None`
    :

`AirbyteConnectorExecutableNotFoundError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector executable not found.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteConnectorFailedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None, exit_code: int | None = None)`
:   Connector failed.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `exit_code: int | None`
    :

`AirbyteConnectorInstallationError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Error when installing the connector.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteConnectorMissingCatalogError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector did not return a catalog.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteConnectorMissingSpecError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector did not return a spec.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteConnectorNotPyPiPublishedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector found, but not published to PyPI.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorRegistryError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

    ### Instance variables

    `connector_name: str | None`
    :

`AirbyteConnectorNotRegisteredError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector not found in registry.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorRegistryError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

    `help_url: str | None`
    :

    ### Instance variables

    `connector_name: str | None`
    :

`AirbyteConnectorReadError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Error when reading from the connector.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteConnectorRegistryError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None)`
:   Error when accessing the connector registry.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteConnectorNotPyPiPublishedError
    * airbyte.exceptions.AirbyteConnectorNotRegisteredError

`AirbyteConnectorSpecFailedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Error when getting spec from the connector.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteConnectorValidationFailedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Connector config validation failed.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

`AirbyteConnectorWriteError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   Error when writing to the connector.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteDuplicateResourcesError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None, resource_type: str | None = None, resource_name: str | None = None)`
:   Process failed because resource name was not unique.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `resource_name: str | None`
    :

    `resource_type: str | None`
    :

`AirbyteError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None)`
:   An error occurred while communicating with the hosted Airbyte instance.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteConnectionError
    * airbyte.exceptions.AirbyteDuplicateResourcesError
    * airbyte.exceptions.AirbyteMissingResourceError
    * airbyte.exceptions.AirbyteMultipleResourcesError
    * airbyte.exceptions.AirbyteWorkspaceMismatchError

    ### Instance variables

    `response: AirbyteApiResponseDuckType | None`
    :   The API response from the failed request.

    `workspace: CloudWorkspace | None`
    :   The workspace where the error occurred.

    `workspace_url: str | None`
    :   The URL to the workspace where the error occurred.

`AirbyteExperimentalFeatureWarning(*args, **kwargs)`
:   Warning whenever using experimental features in PyAirbyte.

    ### Ancestors (in MRO)

    * builtins.FutureWarning
    * builtins.Warning
    * builtins.Exception
    * builtins.BaseException

`AirbyteMissingResourceError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None, resource_type: str | None = None, resource_name_or_id: str | None = None)`
:   Remote Airbyte resources does not exist.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `resource_name_or_id: str | None`
    :

    `resource_type: str | None`
    :

`AirbyteMultipleResourcesError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None, resource_type: str | None = None, resource_name_or_id: str | None = None)`
:   Could not locate the resource because multiple matching resources were found.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `resource_name_or_id: str | None`
    :

    `resource_type: str | None`
    :

`AirbyteNoDataFromConnectorError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None)`
:   No data was provided from the connector.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

`AirbyteStateNotFoundError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None, stream_name: str | None = None, available_streams: list[str] | None = None)`
:   State entry not found.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.KeyError
    * builtins.LookupError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `available_streams: list[str] | None`
    :

    `stream_name: str | None`
    :

`AirbyteStreamNotFoundError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, connector_name: str | None = None, stream_name: str | None = None, available_streams: list[str] | None = None)`
:   Connector stream not found.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `available_streams: list[str] | None`
    :

    `stream_name: str | None`
    :

`AirbyteSubprocessError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, run_args: list[str] | None = None)`
:   Error when running subprocess.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteSubprocessFailedError

    ### Instance variables

    `run_args: list[str] | None`
    :

`AirbyteSubprocessFailedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, run_args: list[str] | None = None, exit_code: int | None = None)`
:   Subprocess failed.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteSubprocessError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `exit_code: int | None`
    :

`AirbyteWorkspaceMismatchError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, response: AirbyteApiResponseDuckType | None = None, workspace: CloudWorkspace | None = None, resource_type: str | None = None, resource_id: str | None = None, expected_workspace_id: str | None = None, actual_workspace_id: str | None = None)`
:   Resource does not belong to the expected workspace.
    
    This error is raised when a resource (connection, source, or destination) is fetched
    from the API and the workspace ID in the response does not match the expected workspace.

    ### Ancestors (in MRO)

    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `actual_workspace_id: str | None`
    :   The workspace ID returned by the API.

    `expected_workspace_id: str | None`
    :   The workspace ID that was expected.

    `resource_id: str | None`
    :   The ID of the resource that was fetched.

    `resource_type: str | None`
    :   The type of resource (e.g., 'connection', 'source', 'destination').

`PyAirbyteCacheError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None)`
:   Error occurred while accessing the cache.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteConnectorConfigurationMissingError
    * airbyte.exceptions.PyAirbyteCacheTableValidationError

`PyAirbyteCacheTableValidationError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, violation: str | None = None)`
:   Cache table validation failed.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteCacheError
    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `violation: str | None`
    :

`PyAirbyteDataLossWarning(*args, **kwargs)`
:   Warning for potential data loss.
    
    Users can ignore this warning by running:
    > warnings.filterwarnings("ignore", category="airbyte.exceptions.PyAirbyteDataLossWarning")

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteWarning
    * builtins.Warning
    * builtins.Exception
    * builtins.BaseException

`PyAirbyteError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None)`
:   Base class for exceptions in Airbyte.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.AirbyteConnectorError
    * airbyte.exceptions.AirbyteConnectorRegistryError
    * airbyte.exceptions.AirbyteError
    * airbyte.exceptions.AirbyteSubprocessError
    * airbyte.exceptions.PyAirbyteCacheError
    * airbyte.exceptions.PyAirbyteInputError
    * airbyte.exceptions.PyAirbyteInternalError
    * airbyte.exceptions.PyAirbyteNameNormalizationError
    * airbyte.exceptions.PyAirbyteSecretNotFoundError

    ### Instance variables

    `context: dict[str, typing.Any] | None`
    :

    `guidance: str | None`
    :

    `help_url: str | None`
    :

    `log_file: pathlib.Path | None`
    :

    `log_text: str | list[str] | None`
    :

    `message: str | None`
    :

    `original_exception: Exception | None`
    :

    `print_full_log: bool`
    :

    ### Methods

    `get_message(self) ‑> str`
    :   Return the best description for the exception.
        
        We resolve the following in order:
        1. The message sent to the exception constructor (if provided).
        2. The first line of the class's docstring.

    `safe_logging_dict(self) ‑> dict[str, typing.Any]`
    :   Return a dictionary of the exception's properties which is safe for logging.
        
        We avoid any properties which could potentially contain PII.

`PyAirbyteInputError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, input_value: str | None = None)`
:   The input provided to PyAirbyte did not match expected validation rules.
    
    This inherits from ValueError so that it can be used as a drop-in replacement for
    ValueError in the PyAirbyte API.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.ValueError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.PyAirbyteNoStreamsSelectedError

    ### Class variables

    `guidance: str | None`
    :

    `help_url: str | None`
    :

    ### Instance variables

    `input_value: str | None`
    :

`PyAirbyteInternalError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None)`
:   An internal error occurred in PyAirbyte.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

    `help_url: str | None`
    :

`PyAirbyteNameNormalizationError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, raw_name: str | None = None, normalization_result: str | None = None)`
:   Error occurred while normalizing a table or column name.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.ValueError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

    `help_url: str | None`
    :

    ### Instance variables

    `normalization_result: str | None`
    :

    `raw_name: str | None`
    :

`PyAirbyteNoStreamsSelectedError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, input_value: str | None = None, connector_name: str | None = None, available_streams: list[str] | None = None)`
:   No streams were selected for the source.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteInputError
    * airbyte.exceptions.PyAirbyteError
    * builtins.ValueError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

    ### Instance variables

    `available_streams: list[str] | None`
    :

    `connector_name: str | None`
    :

`PyAirbyteSecretNotFoundError(guidance: str | None = None, help_url: str | None = None, log_text: str | list[str] | None = None, log_file: Path | None = None, print_full_log: bool = True, context: dict[str, Any] | None = None, message: str | None = None, original_exception: Exception | None = None, secret_name: str | None = None, sources: list[str] | None = None)`
:   Secret not found.

    ### Ancestors (in MRO)

    * airbyte.exceptions.PyAirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Class variables

    `guidance: str | None`
    :

    `help_url: str | None`
    :

    ### Instance variables

    `secret_name: str | None`
    :

    `sources: list[str] | None`
    :

`PyAirbyteWarning(*args, **kwargs)`
:   General warnings from PyAirbyte.

    ### Ancestors (in MRO)

    * builtins.Warning
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte.exceptions.PyAirbyteDataLossWarning