# CDK Migration Guide

## Importing classes
Starting from 1.0.0, CDK classes and functions should be imported directly from `airbyte_cdk` (example: `from airbyte_cdk import HttpStream`). Lower-level `__init__` files are not considered stable, and will be modified without introducing a major release.

Introducing breaking changes to a class or function exported from the top level `__init__.py` will require a major version bump and a migration note to help developer upgrade.

Note that the following packages are not part of the top level init because they require extras dependencies, but are still considered stable:
- `destination.vector_db_based`
- `source.file_based`

The `test` package is not included in the top level init either. The `test` package is still evolving and isn't considered stable.

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
A few classes were deleted from the Airbyte CDK in version 1.0.0:
- AirbyteLogger
- AirbyteSpec
- Authenticators in the `sources.streams.http.auth` module

## Migrating off AirbyteLogger
No connectors should still be using `AirbyteLogger` directly, but the class is still used in some interfaces. The only required change is to update the type annotation from `AirbyteLogger` to `logging.Logger`. For example:

```
def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
```

to

```
def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
```
Don't forget to also update the imports. You can delete `from airbyte_cdk import AirbyteLogger` and replace it with `import logging`.

## Migrating off AirbyteSpec
AirbyteSpec isn't used by any connectors in the repository, and I don't expect any custom connectors to use the class either. This should be a no-op.

## Migrating off Authenticators
Replace usage of authenticators in the `airbyte_cdk.sources.streams.http.auth` module with their sister classes in the `airbyte_cdk.sources.streams.http.requests_native_auth` module.

If any of your streams reference `self.authenticator`, you'll also need to update these references to `self._session.auth` as the authenticator is embedded in the session object.

Here is a [pull request that can serve as an example](https://github.com/airbytehq/airbyte/pull/38065/files).
