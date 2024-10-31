# CDK Migration Guide

## Upgrading to 6.x.x

Version 6.x.x of the CDK introduces concurrent processing of low-code incremental streams. This is breaking because non-manifest only connectors must update their self-managed `run.py` and `source.py` files. This section is intended to clarify how to upgrade a low-code connector to use the Concurrent CDK to sync incremental streams.

> [!NOTE]
> This version introduces parallel processing of only incremental streams.
> It does not include the parallel processing of substreams that rely on a parent stream
> It also does not include processing of full-refresh streams in parallel.

Low-code incremental streams that match any of the following criteria are not supported by concurrent as of this version:
- Uses a custom implementation of the `DatetimeBasedCursor` component
- The `DatetimeBasedCursor` defines a `step` which will partition a stream's request into time intervals AND a 
  `AddedField` / `HttpRequester` / `RecordFilter` that relies on interpolation of the `stream_state` value. See below
  for the complete list

In order to enable concurrency for a low-code connector, the following changes must be made:
- In the connector's `source.py`, change the method signature to accept catalog, config, and state parameters. Change the invocation of `super()` to pass in those new parameters

```python3
class SourceName(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})
```
- In the connector's `run.py`, update it to pass variables

```python3
def _get_source(args: List[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    try:
        return SourceName(
            SourceName.read_catalog(catalog_path) if catalog_path else None,
            SourceName.read_config(config_path) if config_path else None,
            SourceName.read_state(state_path) if state_path else None,
        )
    except Exception as error:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=int(datetime.now().timestamp() * 1000),
                            error=AirbyteErrorTraceMessage(
                                message=f"Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance. Error: {error}",
                                stack_trace=traceback.format_exc(),
                            ),
                        ),
                    )
                )
            ).decode()
        )
        return None


def run():
    _args = sys.argv[1:]
    source = _get_source(_args)
    if source:
        launch(source, _args)
```

- Add the `ConcurrencyLevel` component to the connector's `manifest.yaml` file

```yaml
concurrency_level:
  type: ConcurrencyLevel
  default_concurrency: "{{ config['num_workers'] or 10 }}"
  max_concurrency: 20
```

### Connectors that have streams that cannot be processed concurrently

Connectors that have streams that use `stream_state` during interpolation and must be run synchronously until they are fixed or updated:
- Http Requester
  - `source-insightly`: Uses an DatetimeBasedCursor with a step interval and the HttpRequester has request_parameters relying on `stream_state`. This should be replaced by `step_interval`
  - `source-intercom`: Uses a custom `incremental_sync` component and `stream_state` used as part of the HttpRequester request_body_json. However, because this processed on a single slice, `stream_interval` can be used
- Record Filter
  - `source-chargebee`: Uses a custom `incremental_sync` component and `stream_state` in the RecordFilter condition. However, because this processed on a single slice, `stream_interval` can be used
  - `source-intercom`: Uses a custom `incremental_sync` component and `stream_state` used as part of the RecordFilter condition. However, because this processed on a single slice, `stream_interval` can be used
  - `source-railz`: Uses a custom `incremental_sync` component and `stream_state` used as part of the RecordFilter condition. This also uses multiple one month time intervals and is not currently compatible for concurrent
  - `source-tiktok-marketing`: Contains DatetimeBasedCursor with a step interval and relies on a CustomRecordFilter with a condition relying on `stream_state`. This should be replaced by `stream_interval`
- `AddFields`: No connectors use `stream_state` when performing an additive transformation for a record

To enable concurrency on these streams, `stream_state` should be removed from the interpolated value and replaced
by a thread safe interpolation context like `stream_interval` or `stream_partition`.

### Upgrading manifest-only sources to process incremental streams concurrently

All manifest-only sources are run using the `source-declarative-manifest` which serves as the base image with the common code and flows for connectors that only define a `manifest.yaml` file.

Within this package, to enable concurrent processing:
- Modify `airbyte-cdk` package in `pyproject.toml` to the current version
- In `run.py`, parse all entrypoint arguments into the respective config, catalog, and state objects
- In `run.py`, modify the flow that instantiates a `ManifestDeclarativeSource` from the `__injected_declarative_manifest` to instantiate a `ConcurrentDeclarativeSource`
- In `run.py` modify the `SourceLocalYaml` class to accept config, catalog, and state. And use that in the `YamlDeclarativeSource.__init__`. This should look similar to the migration of sources that are not manifest-only

## Upgrading to 5.0.0

Version 5.0.0 of the CDK updates the `airbyte_cdk.models` dependency to replace Pydantic v2 models with Python `dataclasses`. It also
updates the `airbyte-protocol-models` dependency to a version that uses dataclasses models.

The changes to Airbyte CDK itself are backwards-compatible, but some changes are required if the connector:
- uses the `airbyte_protocol` models directly, or `airbyte_cdk.models`, which points to `airbyte_protocol` models
- uses third-party libraries, such as `pandas`, to read data from sources, which output non-native Python objects that cannot be serialized by the [orjson](https://github.com/ijl/orjson) library.

> [!NOTE]
> All Serializers have omit_none=True parameter that is applied recursively. Thus, all None values are excluded from output.
> This is expected behaviour and does not break anything in protocol.

### Updating direct usage of Pydantic based Airbyte Protocol Models

- If the connector uses Pydantic based Airbyte Protocol Models, the code will need to be updated to reflect the changes `pydantic`.
- It is recommended to import protocol classes not directly by `import airbyte_protocol` statement, but from `airbyte_cdk.models` package.
- It is also recommended to use *-`Serializer` from `airbyte_cdk.models` to manipulate the data or convert to/from JSON.
  These are based on the [serpyco-rs](https://pypi.org/project/serpyco-rs/) library.
- These classes have a `dump` method that converts the model to a dictionary and a `load` method that converts a dictionary to a model.
- The recommended serialization strategy is to pass the dictionary to the `orjson` library when serializing as a JSON string.

E.g.

```python3
import orjson

from airbyte_cdk.models import AirbyteMessage, AirbyteMessageSerializer

# Before (pydantic model message serialization)
AirbyteMessage().model_dump_json()

# After (dataclass model serialization)
orjson.dumps(AirbyteMessageSerializer.dump(AirbyteMessage())).decode()
```

### Updating third-party libraries

For example, if `pandas` outputs data from the source, which has date-time `pandas.Timestamp` object in
it, [Orjson supported Types](https://github.com/ijl/orjson?tab=readme-ov-file#types), these fields should be transformed to native JSON
objects.

```python3
# Before
yield from df.to_dict(orient="records")

# After - Option 1
yield orjson.loads(df.to_json(orient="records", date_format="iso", date_unit="us"))

```


## Upgrading to 4.5.0

In this release, we are no longer supporting the legacy state format in favor of the current per-stream state
format which has been running in production for over 2 years. The impacts to connectors should be minimal, but for
the small number of connectors that instantiate their own `ConnectorStateManager`, the fix to upgrade to the latest
version of the CDK is to stop passing the `stream_instance_map` parameter to the `ConnectorStateManager` constructor.

## Upgrading to 4.1.0
We are unifying the `BackoffStrategy` interface as it currently differs from the Python CDK package to the declarative one. The different is that the interface will require the attempt_count to be passed.

Main impact: This change is mostly internal but we spotted a couple of tests that expect `backoff_time` to not have the `attempt_count` parameter so these tests would fail ([example](https://github.com/airbytehq/airbyte/blob/c9f45a0b85735f58102fcd78385f6f673e731aa6/airbyte-integrations/connectors/source-github/unit_tests/test_stream.py#L99)).

This change should not impact the following classes even though they have a different interface as they accept `kwargs` and  `attempt_count` is currently passed as a keyword argument within the CDK. However, once there is a CDK change where `backoff_time` is called not as a keyword argument, they will fail:
* Zendesk Support: ZendeskSupportBackoffStrategy (this one will be updated shortly after as it is used for CI to validate CDK changes)
* Klaviyo: KlaviyoBackoffStrategy (the logic has been generified so we will remove this custom component shortly after this update)
* GitHub: GithubStreamABCBackoffStrategy and ContributorActivityBackoffStrategy
* Airtable: AirtableBackoffStrategy
* Slack: SlackBackoffStrategy

This change should not impact `WaitUntilMidnightBackoffStrategy` from source-gnews as well but it is interesting to note that its interface is also wrong as it considers the first parameter as a `requests.Response` instead of a `Optional[Union[requests.Response, requests.RequestException]]`.

## Upgrading to 4.0.0

Updated the codebase to utilize new Python syntax features. As a result, support for Python 3.9 has been dropped. The minimum required Python version is now 3.10.

## Upgrading to 3.0.0
Version 3.0.0 of the CDK updates the `HTTPStream` class by reusing the `HTTPClient` under the hood.

- `backoff_time` and `should_retry` methods are removed from HttpStream
- `HttpStreamAdapterHttpStatusErrorHandler` and `HttpStreamAdapterBackoffStrategy` adapters are marked as `deprecated`
- `raise_on_http_errors`, `max_retries`, `max_time`, `retry_factor` are marked as `deprecated`

Exceptions from the `requests` library should no longer be raised when calling `read_records`.
Therefore, catching exceptions should be updated, and error messages might change.
See [Migration of Source Zendesk Support](https://github.com/airbytehq/airbyte/pull/41032/commits/4d3a247f36b9826dcea4b98d30fc19802b03d014) as an example.

### Migration of `should_retry` method
In case the connector uses custom logic for backoff based on the response from the server, a new method `get_error_handler` should be implemented.
This method should return instance of [`ErrorHandler`](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/streams/http/error_handlers/error_handler.py).

### Migration of `backoff_time` method
In case the connector uses custom logic for backoff time calculation, a new method `get_backoff_strategy` should be implemented.
This method should return instance(s) of [`BackoffStrategy`](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/streams/http/error_handlers/backoff_strategy.py).

## Upgrading to 2.0.0
Version 2.0.0 of the CDK updates the `pydantic` dependency to from Pydantic v1 to Pydantic v2. It also
updates the `airbyte-protocol-models` dependency to a version that uses Pydantic V2 models.

The changes to Airbyte CDK itself are backwards-compatible, but some changes are required if the connector:
- uses Pydantic directly, e.g. for its own custom models, or
- uses the `airbyte_protocol` models directly, or `airbyte_cdk.models`, which points to `airbyte_protocol` models, or
- customizes HashableStreamDescriptor, which inherits from a protocol model and has therefore been updated to use Pydantic V2 models.

Some test assertions may also need updating due to changes to default serialization of the protocol models.

### Updating direct usage of Pydantic

If the connector uses pydantic, the code will need to be updated to reflect the change `pydantic` dependency version.
The Pydantic [migration guide](https://docs.pydantic.dev/latest/migration/) is a great resource for any questions that
might arise around upgrade behavior.

#### Using Pydantic V1 models with Pydantic V2
The easiest way to update the code to be compatible without major changes is to update the import statements from
`from pydantic` to `from pydantic.v1`, as Pydantic has kept the v1 module for backwards compatibility.

Some potential gotchas:
  - `ValidationError` must be imported from `pydantic.v1.error_wrappers` instead of `pydantic.v1`
  - `ModelMetaclass` must be imported from `pydantic.v1.main` instead of `pydantic.v1`
  - `resolve_annotations` must be imported from `pydantic.v1.typing` instead of `pydantic.v1`

#### Upgrading to Pydantic V2
To upgrade all the way to V2 proper, Pydantic also offers a [migration tool](https://docs.pydantic.dev/latest/migration/#code-transformation-tool)
to automatically update the code to be compatible with Pydantic V2.

#### Updating assertions
It's possible that a connector might make assertions against protocol models without actually
importing them - for example when testing methods which return `AirbyteStateBlob` or `AnyUrl`.

To resolve this, either compare directly to a model, or `dict()` or `str()` your model accordingly, depending
on if you care most about the serialized output or the model (for a method which returns a model, option 1 is
preferred). For example:

```python
# Before
assert stream_read.slices[1].state[0].stream.stream_state == {"a_timestamp": 123}

# After - Option 1
from airbyte_cdk.models import AirbyteStateBlob
assert stream_read.slices[1].state[0].stream.stream_state == AirbyteStateBlob(a_timestamp=123)

# After - Option 2
assert stream_read.slices[1].state[0].stream.stream_state.dict() == {"a_timestamp": 123}
```


## Upgrading to 1.0.0
Starting from 1.0.0, CDK classes and functions should be imported directly from `airbyte_cdk` (example: `from airbyte_cdk import HttpStream`). Lower-level `__init__` files are not considered stable, and will be modified without introducing a major release.

Introducing breaking changes to a class or function exported from the top level `__init__.py` will require a major version bump and a migration note to help developer upgrade.

Note that the following packages are not part of the top level init because they require extras dependencies, but are still considered stable:
- `destination.vector_db_based`
- `source.file_based`

The `test` package is not included in the top level init either. The `test` package is still evolving and isn't considered stable.


A few classes were deleted from the Airbyte CDK in version 1.0.0:
- AirbyteLogger
- AirbyteSpec
- Authenticators in the `sources.streams.http.auth` module



### Migrating off AirbyteLogger
No connectors should still be using `AirbyteLogger` directly, but the class is still used in some interfaces. The only required change is to update the type annotation from `AirbyteLogger` to `logging.Logger`. For example:

```
def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
```

to

```
def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
```
Don't forget to also update the imports. You can delete `from airbyte_cdk import AirbyteLogger` and replace it with `import logging`.

### Migrating off AirbyteSpec
AirbyteSpec isn't used by any connectors in the repository, and I don't expect any custom connectors to use the class either. This should be a no-op.

### Migrating off Authenticators
Replace usage of authenticators in the `airbyte_cdk.sources.streams.http.auth` module with their sister classes in the `airbyte_cdk.sources.streams.http.requests_native_auth` module.

If any of your streams reference `self.authenticator`, you'll also need to update these references to `self._session.auth` as the authenticator is embedded in the session object.

Here is a [pull request that can serve as an example](https://github.com/airbytehq/airbyte/pull/38065/files).
