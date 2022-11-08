# Changelog

## 0.7.0
Low-code: Allow connector specifications to be defined in the manifest

## 0.6.0
Low-code: Add support for monthly and yearly incremental updates for `DatetimeStreamSlicer`

## 0.5.4
Low-code: Get response.json in a safe way

## 0.5.3
Low-code: Replace EmptySchemaLoader with DefaultSchemaLoader to retain backwards compatibility
Low-code: Evaluate backoff strategies at runtime

## 0.5.2
Low-code: Allow for read even when schemas are not defined for a connector yet

## 0.4.2
Low-code: Fix off by one error with the stream slicers

## 0.4.1
Low-code: Fix a few bugs with the stream slicers

## 0.4.0
Low-code: Add support for custom error messages on error response filters

## 0.3.0
Publish python typehints via `py.typed` file. 

## 0.2.3
- Propagate options to InterpolatedRequestInputProvider

## 0.2.2
- Report config validation errors as failed connection status during `check`.
- Report config validation errors as `config_error` failure type.

## 0.2.1

- Low-code: Always convert stream slices output to an iterator

## 0.2.0

- Replace caching method: VCR.py -> requests-cache with SQLite backend

## 0.1.104

- Protocol change: `supported_sync_modes` is now a required properties on AirbyteStream. [#15591](https://github.com/airbytehq/airbyte/pull/15591)

## 0.1.103

- Low-code: added hash filter to jinja template

## 0.1.102

- Low-code: Fix check for streams that do not define a stream slicer

## 0.1.101

- Low-code: $options do not overwrite parameters that are already set

## 0.1.100

- Low-code: Pass stream_slice to read_records when reading from CheckStream

## 0.1.99

- Low-code: Fix default stream schema loader

## 0.1.98

- Low-code: Expose WaitUntilTimeFromHeader strategy and WaitTimeFromHeader as component type

## 0.1.97

- Revert 0.1.96

## 0.1.96

- Improve error for returning non-iterable from connectors parse_response

## 0.1.95

- Low-code: Expose PageIncrement strategy as component type

## 0.1.94

- Low-code: Stream schema loader has a default value and can be omitted

## 0.1.93

- Low-code: Standardize slashes in url_base and path

## 0.1.92

- Low-code: Properly propagate $options to array items
- Low-code: Log request and response when running check operation in debug mode

## 0.1.91

- Low-code: Rename LimitPaginator to DefaultPaginator and move page_size field to PaginationStrategy

## 0.1.90

- Fix error when TypeTransformer tries to warn about invalid transformations in arrays

## 0.1.89

- Fix: properly emit state when a stream has empty slices, provided by an iterator

## 0.1.88

- Bugfix: Evaluate `response.text` only in debug mode

## 0.1.87

- During incremental syncs allow for streams to emit state messages in the per-stream format

## 0.1.86

- TypeTransformer now converts simple types to array of simple types
- TypeTransformer make warning message more informative

## 0.1.85

- Make TypeTransformer more robust to incorrect incoming records

## 0.1.84

- Emit legacy format when state is unspecified for read override connectors

## 0.1.83

- Fix per-stream to send legacy format for connectors that override read

## 0.1.82

- Freeze dataclasses-jsonschema to 2.15.1

## 0.1.81

- Fix regression in `_checkpoint_state` arg

## Unreleased

- Update Airbyte Protocol model to support protocol_version

## 0.1.80

- Add NoAuth to declarative registry and auth parse bug fix

## 0.1.79

- Fix yaml schema parsing when running from docker container

## 0.1.78

- Fix yaml config parsing when running from docker container

## 0.1.77

- Add schema validation for declarative YAML connector configs

## 0.1.76

- Bugfix: Correctly set parent slice stream for sub-resource streams

## 0.1.75

- Improve `filter_secrets` skip empty secret

## 0.1.74

- Replace JelloRecordExtractor with DpathRecordExtractor

## 0.1.73

- Bugfix: Fix bug in DatetimeStreamSlicer's parsing method

## 0.1.72

- Bugfix: Fix bug in DatetimeStreamSlicer's format method

## 0.1.71

- Refactor declarative package to dataclasses
- Bugfix: Requester header always converted to string
- Bugfix: Reset paginator state between stream slices
- Bugfix: Record selector handles single records

## 0.1.70

- Bugfix: DatetimeStreamSlicer cast interpolated result to string before converting to datetime
- Bugfix: Set stream slicer's request options in SimpleRetriever

## 0.1.69

- AbstractSource emits a state message when reading incremental even if there were no stream slices to process.

## 0.1.68

- Replace parse-time string interpolation with run-time interpolation in YAML-based sources

## 0.1.67

- Add support declarative token authenticator.

## 0.1.66

- Call init_uncaught_exception_handler from AirbyteEntrypoint.__init__ and Destination.run_cmd
- Add the ability to remove & add records in YAML-based sources

## 0.1.65

- Allow for detailed debug messages to be enabled using the --debug command.

## 0.1.64

- Add support for configurable oauth request payload and declarative oauth authenticator.

## 0.1.63

- Define `namespace` property on the `Stream` class inside `core.py`.

## 0.1.62

Bugfix: Correctly obfuscate nested secrets and secrets specified inside oneOf blocks inside the connector's spec.

## 0.1.61

- Remove legacy sentry code

## 0.1.60

- Add `requests.exceptions.ChunkedEncodingError` to transient errors so it could be retried

## 0.1.59

- Add `Stream.get_error_display_message()` to retrieve user-friendly messages from exceptions encountered while reading streams.
- Add default error error message retrieval logic for `HTTPStream`s following common API patterns.

## 0.1.58

`TypeTransformer.default_convert` catch `TypeError`

## 0.1.57

Update protocol models to support per-stream state: [#12829](https://github.com/airbytehq/airbyte/pull/12829).

## 0.1.56

- Update protocol models to include `AirbyteTraceMessage`
- Emit an `AirbyteTraceMessage` on uncaught exceptions
- Add `AirbyteTracedException`

## 0.1.55

Add support for reading the spec from a YAML file (`spec.yaml`)

## 0.1.54

- Add ability to import `IncrementalMixin` from `airbyte_cdk.sources.streams`.
- Bumped minimum supported Python version to 3.9.

## 0.1.53

Remove a false positive error logging during the send process.

## 0.1.52

Fix BaseBackoffException constructor

## 0.1.50

Improve logging for Error handling during send process.

## 0.1.49

Add support for streams with explicit state attribute.

## 0.1.48

Fix type annotations.

## 0.1.47

Fix typing errors.

## 0.1.45

Integrate Sentry for performance and errors tracking.

## 0.1.44

Log http response status code and its content.

## 0.1.43

Fix logging of unhandled exceptions: print stacktrace.

## 0.1.42

Add base pydantic model for connector config and schemas.

## 0.1.41

Fix build error

## 0.1.40

Filter airbyte_secrets values at logger and other logging refactorings.

## 0.1.39

Add `__init__.py` to mark the directory `airbyte_cdk/utils` as a package.

## 0.1.38

Improve URL-creation in CDK. Changed to using `urllib.parse.urljoin()`.

## 0.1.37

Fix `emitted_at` from `seconds * 1000` to correct milliseconds.

## 0.1.36

Fix broken logger in streams: add logger inheritance for streams from `airbyte`.

## 0.1.35

Fix false warnings on record transform.

## 0.1.34

Fix logging inside source and streams

## 0.1.33

Resolve $ref fields for discover json schema.

## 0.1.32

- Added Sphinx docs `airbyte-cdk/python/reference_docs` module.
- Added module documents at `airbyte-cdk/python/sphinx-docs.md`.
- Added Read the Docs publishing configuration at `.readthedocs.yaml`.

## 0.1.31

Transforming Python log levels to Airbyte protocol log levels

## 0.1.30

Updated OAuth2Specification.rootObject type in airbyte_protocol to allow string or int

## 0.1.29

Fix import logger error

## 0.1.28

Added `check_config_against_spec` parameter to `Connector` abstract class
to allow skipping validating the input config against the spec for non-`check` calls

## 0.1.27

Improving unit test for logger

## 0.1.26

Use python standard logging instead of custom class

## 0.1.25

Modified `OAuth2Specification` model, added new fields: `rootObject` and `oauthFlowOutputParameters`

## 0.1.24

Added Transform class to use for mutating record value types so they adhere to jsonschema definition.

## 0.1.23

Added the ability to use caching for efficient synchronization of nested streams.

## 0.1.22

Allow passing custom headers to request in `OAuth2Authenticator.refresh_access_token()`: https://github.com/airbytehq/airbyte/pull/6219

## 0.1.21

Resolve nested schema references and move external references to single schema definitions.

## 0.1.20

- Allow using `requests.auth.AuthBase` as authenticators instead of custom CDK authenticators.
- Implement Oauth2Authenticator, MultipleTokenAuthenticator and TokenAuthenticator authenticators.
- Add support for both legacy and requests native authenticator to HttpStream class.

## 0.1.19

No longer prints full config files on validation error to prevent exposing secrets to log file: https://github.com/airbytehq/airbyte/pull/5879

## 0.1.18

Fix incremental stream not saved state when internal limit config set.

## 0.1.17

Fix mismatching between number of records actually read and number of records in logs by 1: https://github.com/airbytehq/airbyte/pull/5767

## 0.1.16

Update generated AirbyteProtocol models to contain [Oauth changes](https://github.com/airbytehq/airbyte/pull/5776).

## 0.1.15

Add \_limit and \_page_size as internal config parameters for SAT

## 0.1.14

If the input config file does not comply with spec schema, raise an exception instead of `system.exit`.

## 0.1.13

Fix defect with user defined backoff time retry attempts, number of retries logic fixed

## 0.1.12

Add raise_on_http_errors, max_retries, retry_factor properties to be able to ignore http status errors and modify retry time in HTTP stream

## 0.1.11

Add checking specified config againt spec for read, write, check and discover commands

## 0.1.10

Add `MultipleTokenAuthenticator` class to allow cycling through a list of API tokens when making HTTP requests

## 0.1.8

Allow to fetch primary key info from singer catalog

## 0.1.7

Allow to use non-JSON payloads in request body for http source

## 0.1.6

Add abstraction for creating destinations.

Fix logging of the initial state.

## 0.1.5

Allow specifying keyword arguments to be sent on a request made by an HTTP stream: https://github.com/airbytehq/airbyte/pull/4493

## 0.1.4

Allow to use Python 3.7.0: https://github.com/airbytehq/airbyte/pull/3566

## 0.1.2

Fix an issue that caused infinite pagination: https://github.com/airbytehq/airbyte/pull/3366

## 0.1.1

Initial Release
