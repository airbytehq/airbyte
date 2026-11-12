# source-e2e-test: Contributor notes

## Mock JSON record generation

The connector uses `airbytehq/jsongenerator` to generate random JSON records from the configured JSON schema. This library is forked from `jimblackler/jsongenerator` and is licensed under Apache 2.0.

This generator has two important constraints:

- It uses JavaScript inside Java through `org.mozilla:rhino-engine` and fetches remote JavaScript snippets in `PatternReverser`.
- It does not support per-field customization. Generated JSON objects can look garbled.

## Cloud variant

The cloud version of this connector only allows `CONTINUOUS FEED` mode. The legacy `INFINITE FEED` and `EXCEPTION AFTER N` modes are excluded from cloud because the catalog is not customized for those modes and the connector should not emit infinite records in cloud.

If you change `CONTINUOUS FEED` mode, update and publish the cloud variant as well.
