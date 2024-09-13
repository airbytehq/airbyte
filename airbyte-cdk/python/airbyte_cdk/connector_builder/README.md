# Connector Builder Backend

This is the backend for requests from the
[Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview/).

## Local development

### Locally running the Connector Builder backend

```bash
python main.py read --config path/to/config --catalog path/to/catalog
```

Note:

- Requires the keys `__injected_declarative_manifest` and `__command` in its config, where
  `__injected_declarative_manifest` is a JSON manifest and `__command` is one of the commands
  handled by the ConnectorBuilderHandler (`stream_read` or `resolve_manifest`), i.e.

```json
{
  "config": <normal config>,
  "__injected_declarative_manifest": {...},
  "__command": <"resolve_manifest" | "test_read">
}
```

\*See
[ConnectionSpecification](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#actor-specification)
for details on the `"config"` key if needed.

- When the `__command` is `resolve_manifest`, the argument to `catalog` should be an empty string.
- The config can optionally contain an object under the `__test_read_config` key which can define
  custom test read limits with `max_records`, `max_slices`, and `max_pages_per_slice` properties.
  All custom limits are optional; a default will be used for any limit that is not provided.

### Locally running the docker image

#### Build

First, make sure you build the latest Docker image:

```bash
docker build -t airbyte/source-declarative-manifest:dev .
```

#### Run

Then run any of the connector commands as follows:

```bash
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-declarative-manifest:dev read --config /secrets/config.json
```
