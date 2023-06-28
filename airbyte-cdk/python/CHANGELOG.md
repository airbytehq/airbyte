# Changelog

## 0.44.0
Support data feed like incremental syncs

## 0.43.3
Fix return type of RecordFilter: changed from generator to list

## 0.43.2
Connector builder module: serialize request body as string

## 0.43.1
Fix availability check to handle HttpErrors which happen during slice extraction

## 0.43.0
Refactoring declarative state management

## 0.42.1
Error message on state per partition state discrepancy

## 0.42.0
Supporting state per partition given incremental sync and partition router

## 0.41.0
Use x-www-urlencoded for access token refresh requests

## 0.40.5
Replace  with  when making oauth calls

## 0.40.4
Emit messages using message repository

## 0.40.3
Add utils for inferring datetime formats

## 0.40.2
Add a metadata field to the declarative component schema

## 0.40.1
make DatetimeBasedCursor.end_datetime optional

## 0.40.0
Remove SingleUseRefreshTokenOAuthAuthenticator from low code CDK and add generic injection capabilities to ApiKeyAuthenticator

## 0.39.4
Connector builder: add latest connector config control message to read calls

## 0.39.3
Add refresh token update capabilities to OAuthAuthenticator

## 0.39.2
Make step and cursor_granularity optional

## 0.39.1
Improve connector builder error messages

## 0.39.0
Align schema generation in SchemaInferrer with Airbyte platform capabilities

## 0.38.0
Allow nested objects in request_body_json

## 0.37.0
low-code: Make refresh token in oauth authenticator optional

## 0.36.5
Unfreeze requests version and test new pipeline

## 0.36.4
low-code: use jinja sandbox and restrict some methods

## 0.36.3
pin the version of the requests library

## 0.36.2
Support parsing non UTC dates and Connector Builder set slice descriptor

## 0.36.1
low-code: fix add field transformation when running from the connector builder

## 0.36.0
Emit stream status messages

## 0.35.4
low-code: remove now_local() macro because it's too unpredictable

## 0.35.3
low-code: alias stream_interval and stream_partition to stream_slice in jinja context

## 0.35.2
Connector builder scrubs secrets from raw request and response

## 0.35.1
low-code: Add title, description, and examples for all fields in the manifest schema

## 0.35.0
low-code: simplify session token authenticator interface

## 0.34.3
low-code: fix typo in ManifestDeclarativeSource

## 0.34.2
Emit slice log messages when running the connector builder

## 0.34.1
set slice and pages limit when reading from the connector builder module

## 0.34.0
Low-Code CDK: Enable use of SingleUseRefreshTokenAuthenticator

## 0.33.2
low-code: fix duplicate stream slicer update

## 0.33.1
Low-Code CDK: make RecordFilter.filter_records as generator

## 0.33.0
Enable oauth flow for low-code connectors

## 0.32.0
Remove unexpected error swallowing on abstract source's check method

## 0.31.1
connector builder: send stacktrace when error on read

## 0.31.0
Add connector builder module for handling Connector Builder server requests

## 0.30.4
CDK's read command handler supports Connector Builder list_streams requests

## 0.30.3
Fix reset pagination issue on test reads

## 0.30.2
* Low-code CDK: Override refresh_access_token logic DeclarativeOAuthAuthenticator

## 0.30.1
Releasing using the new release flow. No change to the CDK per se

## 0.30.0
OAuth: retry refresh access token requests

## 0.29.3
Low-Code CDK: duration macro added

## 0.29.2
support python3.8

## 0.29.1
Publishing Docker image for source-declarative-manifest

## 0.29.0
**Breaking changes: We have promoted the low-code CDK to Beta. This release contains a number of breaking changes intended to improve the overall usability of the language by reorganizing certain concepts, renaming, reducing some field duplication, and removal of fields that are seldom used.**

The changes are: 
* Deprecated the concept of Stream Slicers in favor of two individual concepts: Incremental Syncs, and Partition Routers: 
  * Stream will define an `incremental_sync` field which is responsible for defining how the connector should support incremental syncs using a cursor field. `DatetimeStreamSlicer` has been renamed to `DatetimeBasedCursor` and can be used for this field.
  * `Retriever`s will now define a `partition_router` field. The remaining slicers are now called `SubstreamPartitionRouter` and `ListPartitionRouter`, both of which can be used here as they already have been.
  * The `CartesianProductStreamSlicer` because `partition_router` can accept a list of values and will generate that same cartesian product by default.
* `$options` have been renamed to `$parameters`
* Changed the notation for component references to the JSON schema notation (`$ref: "#/definitions/requester"`)
* `DefaultPaginator` no longer has a `url_base` field. Moving forward, paginators will derive the `url_base` from the `HttpRequester`. There are some unique cases for connectors that implement a custom `Retriever`.
* `primary_key` and `name` no longer need to be defined on `Retriever`s or `Requester`s. They will be derived from the stream’s definition
* Streams no longer define a `stream_cursor_field` and will derive it from the `incremental_sync` component. `checkpoint_interval` has also been deprecated
* DpathExtractor `field_pointer` has been renamed to `field_path`
* `RequestOption` can no longer be used with with `inject_into` set to `path`. There is now a dedicated `RequestPath` component moving forward.

## 0.28.1
Low-Code CDK: fix signature _parse_records_and_emit_request_and_responses

## 0.28.0
Low-Code: improve day_delta macro and MinMaxDatetime component

## 0.27.0
Make HttpAvailabilityStrategy default for HttpStreams

## 0.26.0
Low-Code CDK: make DatetimeStreamSlicer.step as InterpolatedString

## 0.25.2
Low-Code: SubstreamSlicer.parent_key - dpath support added

## 0.25.1
Fix issue when trying to log stream slices that are non-JSON-serializable

## 0.25.0
Use dpath.util.values method to parse response with nested lists

## 0.24.0
Use dpath.util.values method to parse response with nested lists

## 0.23.0
Limiting the number of HTTP requests during a test read

## 0.22.0
Surface the resolved manifest in the CDK

## 0.21.0
Add AvailabilityStrategy concept and use check_availability within CheckStream

## 0.20.2
Add missing package in previous patch release

## 0.20.1
Handle edge cases for CheckStream - checking connection to empty stream, and checking connection to substream with no parent records

## 0.20.0
Low-Code: Refactor low-code to use Pydantic model based manifest parsing and component creation

## 0.19.1
Low-code: Make documentation_url in the Spec be optional

## 0.19.0
Low-Code: Handle forward references in manifest

## 0.18.1
Allow for CustomRequester to be defined within declarative manifests

## 0.18.0
Adding `cursor_granularity` to the declarative API of DatetimeStreamSlicer

## 0.17.0
Add utility class to infer schemas from real records

## 0.16.3
Do not eagerly refresh access token in `SingleUseRefreshTokenOauth2Authenticator` [#20923](https://github.com/airbytehq/airbyte/pull/20923)

## 0.16.2
Fix the naming of OAuthAuthenticator

## 0.16.1
Include declarative_component_schema.yaml in the publish to PyPi

## 0.16.0
Start validating low-code manifests using the declarative_component_schema.yaml file

## 0.15.0
Reverts additions from versions 0.13.0 and 0.13.3.

## 0.14.0
Low-code: Add token_expiry_date_format to OAuth Authenticator. Resolve ref schema

## 0.13.3
Fixed `StopIteration` exception for empty streams while `check_availability` runs.

## 0.13.2
Low-code: Enable low-code CDK users to specify schema inline in the manifest

## 0.13.1
Low-code: Add `SessionTokenAuthenticator`

## 0.13.0
Add `Stream.check_availability` and `Stream.AvailabilityStrategy`. Make `HttpAvailabilityStrategy` the default `HttpStream.AvailabilityStrategy`.

## 0.12.4
Lookback window should applied when a state is supplied as well

## 0.12.3
Low-code: Finally, make `OffsetIncrement.page_size` interpolated string or int

## 0.12.2
Revert breaking change on `read_config` while keeping the improvement on the error message

## 0.12.0
Improve error readability when reading JSON config files

## 0.11.3
Low-code: Log response error message on failure

## 0.11.2
Low-code: Include the HTTP method used by the request in logging output of the `airbyte-cdk`

## 0.11.1
Low-code: Fix the component manifest schema to and validate check instead of checker

## 0.11.0
Declare a new authenticator `SingleUseRefreshTokenOauth2Authenticator` that can perform connector configuration mutation and emit `AirbyteControlMessage.ConnectorConfig`.

## 0.10.0
Low-code: Add `start_from_page` option to a PageIncrement class

## 0.9.5
Low-code: Add jinja macro `format_datetime`

## 0.9.4
Low-code: Fix reference resolution for connector builder

## 0.9.3
Low-code: Avoid duplicate HTTP query in `simple_retriever`

## 0.9.2
Low-code: Make `default_paginator.page_token_option` optional

## 0.9.1
Low-code: Fix filtering vars in `InterpolatedRequestInputProvider.eval_request_inputs`

## 0.9.0
Low-code: Allow `grant_type` to be specified for OAuthAuthenticator

## 0.8.1
Low-code: Don't update cursor for non-record messages and fix default loader for connector builder manifests

## 0.8.0
Low-code: Allow for request and response to be emitted as log messages

## 0.7.1
Low-code: Decouple yaml manifest parsing from the declarative source implementation

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
