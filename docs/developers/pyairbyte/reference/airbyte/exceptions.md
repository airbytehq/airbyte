---
sidebar_label: exceptions
title: airbyte.exceptions
---

All exceptions used in the PyAirbyte.

This design is modeled after structlog&#x27;s exceptions, in that we bias towards auto-generated
property prints rather than sentence-like string concatenation.

E.g. Instead of this:

&gt; `Subprocess failed with exit code '1'`

We do this:

&gt; `Subprocess failed. (exit_code=1)`

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
- Use the &#x27;from&#x27; syntax to chain exceptions when it is helpful to do so.
  E.g. `raise AirbyteConnectorNotFoundError(...) from FileNotFoundError(connector_path)`
- Any exception that adds a new property should also be decorated as `@dataclass`.

## annotations

## logging

## dataclass

## Path

## indent

## TYPE\_CHECKING

## Any

## AIRBYTE\_PRINT\_FULL\_ERROR\_LOGS

#### NEW\_ISSUE\_URL

#### DOCS\_URL\_BASE

#### DOCS\_URL

#### VERTICAL\_SEPARATOR

## PyAirbyteError Objects

```python
@dataclass
class PyAirbyteError(Exception)
```

Base class for exceptions in Airbyte.

#### guidance

#### help\_url

#### log\_text

#### log\_file

#### print\_full\_log

#### context

#### message

#### original\_exception

#### get\_message

```python
def get_message() -> str
```

Return the best description for the exception.

We resolve the following in order:
1. The message sent to the exception constructor (if provided).
2. The first line of the class&#x27;s docstring.

#### \_\_str\_\_

```python
def __str__() -> str
```

Return a string representation of the exception.

#### \_\_repr\_\_

```python
def __repr__() -> str
```

Return a string representation of the exception.

#### safe\_logging\_dict

```python
def safe_logging_dict() -> dict[str, Any]
```

Return a dictionary of the exception&#x27;s properties which is safe for logging.

We avoid any properties which could potentially contain PII.

## PyAirbyteInternalError Objects

```python
@dataclass
class PyAirbyteInternalError(PyAirbyteError)
```

An internal error occurred in PyAirbyte.

#### guidance

#### help\_url

## PyAirbyteInputError Objects

```python
@dataclass
class PyAirbyteInputError(PyAirbyteError, ValueError)
```

The input provided to PyAirbyte did not match expected validation rules.

This inherits from ValueError so that it can be used as a drop-in replacement for
ValueError in the PyAirbyte API.

#### guidance

#### help\_url

#### input\_value

## PyAirbyteNoStreamsSelectedError Objects

```python
@dataclass
class PyAirbyteNoStreamsSelectedError(PyAirbyteInputError)
```

No streams were selected for the source.

#### guidance

#### connector\_name

#### available\_streams

## PyAirbyteNameNormalizationError Objects

```python
@dataclass
class PyAirbyteNameNormalizationError(PyAirbyteError, ValueError)
```

Error occurred while normalizing a table or column name.

#### guidance

#### help\_url

#### raw\_name

#### normalization\_result

## PyAirbyteCacheError Objects

```python
class PyAirbyteCacheError(PyAirbyteError)
```

Error occurred while accessing the cache.

## PyAirbyteCacheTableValidationError Objects

```python
@dataclass
class PyAirbyteCacheTableValidationError(PyAirbyteCacheError)
```

Cache table validation failed.

#### violation

## AirbyteConnectorConfigurationMissingError Objects

```python
@dataclass
class AirbyteConnectorConfigurationMissingError(PyAirbyteCacheError)
```

Connector is missing configuration.

#### connector\_name

## AirbyteSubprocessError Objects

```python
@dataclass
class AirbyteSubprocessError(PyAirbyteError)
```

Error when running subprocess.

#### run\_args

## AirbyteSubprocessFailedError Objects

```python
@dataclass
class AirbyteSubprocessFailedError(AirbyteSubprocessError)
```

Subprocess failed.

#### exit\_code

## AirbyteConnectorRegistryError Objects

```python
class AirbyteConnectorRegistryError(PyAirbyteError)
```

Error when accessing the connector registry.

## AirbyteConnectorNotRegisteredError Objects

```python
@dataclass
class AirbyteConnectorNotRegisteredError(AirbyteConnectorRegistryError)
```

Connector not found in registry.

#### connector\_name

#### guidance

#### help\_url

## AirbyteConnectorNotPyPiPublishedError Objects

```python
@dataclass
class AirbyteConnectorNotPyPiPublishedError(AirbyteConnectorRegistryError)
```

Connector found, but not published to PyPI.

#### connector\_name

#### guidance

## AirbyteConnectorError Objects

```python
@dataclass
class AirbyteConnectorError(PyAirbyteError)
```

Error when running the connector.

#### connector\_name

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

Set the log file path for the connector.

#### \_get\_log\_file

```python
def _get_log_file() -> Path | None
```

Return the log file path for the connector.

## AirbyteConnectorExecutableNotFoundError Objects

```python
class AirbyteConnectorExecutableNotFoundError(AirbyteConnectorError)
```

Connector executable not found.

## AirbyteConnectorInstallationError Objects

```python
class AirbyteConnectorInstallationError(AirbyteConnectorError)
```

Error when installing the connector.

## AirbyteConnectorReadError Objects

```python
class AirbyteConnectorReadError(AirbyteConnectorError)
```

Error when reading from the connector.

## AirbyteConnectorWriteError Objects

```python
class AirbyteConnectorWriteError(AirbyteConnectorError)
```

Error when writing to the connector.

## AirbyteConnectorSpecFailedError Objects

```python
class AirbyteConnectorSpecFailedError(AirbyteConnectorError)
```

Error when getting spec from the connector.

## AirbyteConnectorDiscoverFailedError Objects

```python
class AirbyteConnectorDiscoverFailedError(AirbyteConnectorError)
```

Error when running discovery on the connector.

## AirbyteNoDataFromConnectorError Objects

```python
class AirbyteNoDataFromConnectorError(AirbyteConnectorError)
```

No data was provided from the connector.

## AirbyteConnectorMissingCatalogError Objects

```python
class AirbyteConnectorMissingCatalogError(AirbyteConnectorError)
```

Connector did not return a catalog.

## AirbyteConnectorMissingSpecError Objects

```python
class AirbyteConnectorMissingSpecError(AirbyteConnectorError)
```

Connector did not return a spec.

## AirbyteConnectorValidationFailedError Objects

```python
class AirbyteConnectorValidationFailedError(AirbyteConnectorError)
```

Connector config validation failed.

#### guidance

## AirbyteConnectorCheckFailedError Objects

```python
class AirbyteConnectorCheckFailedError(AirbyteConnectorError)
```

Connector check failed.

#### guidance

## AirbyteConnectorFailedError Objects

```python
@dataclass
class AirbyteConnectorFailedError(AirbyteConnectorError)
```

Connector failed.

#### exit\_code

## AirbyteStreamNotFoundError Objects

```python
@dataclass
class AirbyteStreamNotFoundError(AirbyteConnectorError)
```

Connector stream not found.

#### stream\_name

#### available\_streams

## AirbyteStateNotFoundError Objects

```python
@dataclass
class AirbyteStateNotFoundError(AirbyteConnectorError, KeyError)
```

State entry not found.

#### stream\_name

#### available\_streams

## PyAirbyteSecretNotFoundError Objects

```python
@dataclass
class PyAirbyteSecretNotFoundError(PyAirbyteError)
```

Secret not found.

#### guidance

#### help\_url

#### secret\_name

#### sources

## AirbyteError Objects

```python
@dataclass
class AirbyteError(PyAirbyteError)
```

An error occurred while communicating with the hosted Airbyte instance.

#### response

The API response from the failed request.

#### workspace

The workspace where the error occurred.

#### workspace\_url

```python
@property
def workspace_url() -> str | None
```

The URL to the workspace where the error occurred.

## AirbyteConnectionError Objects

```python
@dataclass
class AirbyteConnectionError(AirbyteError)
```

An connection error occurred while communicating with the hosted Airbyte instance.

#### connection\_id

The connection ID where the error occurred.

#### job\_id

The job ID where the error occurred (if applicable).

#### job\_status

The latest status of the job where the error occurred (if applicable).

#### connection\_url

```python
@property
def connection_url() -> str | None
```

The web URL to the connection where the error occurred.

#### job\_history\_url

```python
@property
def job_history_url() -> str | None
```

The URL to the job history where the error occurred.

#### job\_url

```python
@property
def job_url() -> str | None
```

The URL to the job where the error occurred.

## AirbyteConnectionSyncError Objects

```python
@dataclass
class AirbyteConnectionSyncError(AirbyteConnectionError)
```

An error occurred while executing the remote Airbyte job.

## AirbyteWorkspaceMismatchError Objects

```python
@dataclass
class AirbyteWorkspaceMismatchError(AirbyteError)
```

Resource does not belong to the expected workspace.

This error is raised when a resource (connection, source, or destination) is fetched
from the API and the workspace ID in the response does not match the expected workspace.

#### resource\_type

The type of resource (e.g., &#x27;connection&#x27;, &#x27;source&#x27;, &#x27;destination&#x27;).

#### resource\_id

The ID of the resource that was fetched.

#### expected\_workspace\_id

The workspace ID that was expected.

#### actual\_workspace\_id

The workspace ID returned by the API.

## AirbyteConnectionSyncTimeoutError Objects

```python
@dataclass
class AirbyteConnectionSyncTimeoutError(AirbyteConnectionSyncError)
```

An timeout occurred while waiting for the remote Airbyte job to complete.

#### timeout

The timeout in seconds that was reached.

## AirbyteMissingResourceError Objects

```python
@dataclass
class AirbyteMissingResourceError(AirbyteError)
```

Remote Airbyte resources does not exist.

#### resource\_type

#### resource\_name\_or\_id

## AirbyteDuplicateResourcesError Objects

```python
@dataclass
class AirbyteDuplicateResourcesError(AirbyteError)
```

Process failed because resource name was not unique.

#### resource\_type

#### resource\_name

## AirbyteMultipleResourcesError Objects

```python
@dataclass
class AirbyteMultipleResourcesError(AirbyteError)
```

Could not locate the resource because multiple matching resources were found.

#### resource\_type

#### resource\_name\_or\_id

## AirbyteExperimentalFeatureWarning Objects

```python
class AirbyteExperimentalFeatureWarning(FutureWarning)
```

Warning whenever using experimental features in PyAirbyte.

## PyAirbyteWarning Objects

```python
class PyAirbyteWarning(Warning)
```

General warnings from PyAirbyte.

## PyAirbyteDataLossWarning Objects

```python
class PyAirbyteDataLossWarning(PyAirbyteWarning)
```

Warning for potential data loss.

Users can ignore this warning by running:
&gt; warnings.filterwarnings(&quot;ignore&quot;, category=&quot;airbyte.exceptions.PyAirbyteDataLossWarning&quot;)

