# Dewey Destination

Airbyte destination connector for [Dewey](https://meetdewey.com), the managed RAG service.

Each Airbyte stream is mapped to a Dewey collection. Records are uploaded as JSON
documents and Dewey runs the chunking, embedding, and indexing pipeline server-side.
The connector tags every uploaded document with `airbyte_stream:<stream>` and
`airbyte_pk:<primary_key>` so that overwrite and append-dedup syncs can locate prior
versions for deletion.

## Local development

### Prerequisites

Python 3.9–3.11.

```bash
poetry install --with dev
```

### Configuration

Create `secrets/config.json` (gitignored):

```json
{
  "api_key": "dwy_test_...",
  "stream_collections": {
    "default__products": "col_xxxxxxxx"
  }
}
```

### Run locally

```bash
python main.py spec
python main.py check --config secrets/config.json
python main.py write --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Tests

```bash
poetry run pytest unit_tests
DEWEY_API_KEY=dwy_test_... poetry run pytest -s integration_tests
```

The integration test reads `DEWEY_API_KEY` from the environment, creates a fresh
collection for each run, and deletes it on teardown.
