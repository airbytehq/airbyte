# CDK Migration Guide

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
Don't forget to also update the imports. You can delete `from airbyte_cdk import AirbyteLogger` and replace it with `import logging`

## Migrating off AirbyteSpec
AirbyteSpec isn't used by any connectors in the repository, and I don't expect any custom connectors to use the class either. This should be a no-op.

## Migrating off Authenticators
Replace usage of authenticators in the `airbyte_cdk.sources.streams.http.auth` module with their sister classes in the `airbyte_cdk.sources.streams.http.requests_native_auth` module.

If any of your streams reference `self.authenticator`, you'll also need to update these references to `self._session.auth` as the authenticator is embedded in the session object.

Here is a [pull request that can serve as an example](https://github.com/airbytehq/airbyte/pull/38065/files).
