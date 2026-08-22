# Source ComfyUI

Airbyte source connector for ComfyUI Cloud API. Extracts generation jobs, assets, models, nodes, and system data from ComfyUI Cloud into any Airbyte destination.

## Streams

| Stream | Endpoint | Sync Mode | Cursor Field | Description |
|:-------|:---------|:----------|:-------------|:------------|
| `jobs` | `GET /api/jobs` | Incremental | `create_time` | Generation job history with status, timing, workflow references |
| `job_details` | `GET /api/jobs/{job_id}` | Incremental | `create_time` | Full job data including workflow graph, outputs, execution metadata |
| `assets` | `GET /api/assets` | Incremental | `created_at` | User assets with tags, metadata, sizes, preview URLs |
| `models` | `GET /api/models/{folder}` | Full Refresh | — | Available AI model catalog by folder |
| `nodes` | `GET /api/object_info` | Full Refresh | — | Node type catalog with inputs, outputs, categories |
| `system_stats` | `GET /api/system_stats` | Full Refresh | — | System info: OS, GPU, VRAM, ComfyUI version |

## Configuration

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `api_key` | string | Yes | ComfyUI Cloud API key from [platform.comfy.org](https://platform.comfy.org/profile/api-keys) |
| `base_url` | string | No | API base URL (default: `https://cloud.comfy.org`) |

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the connector
python -m source_comfyui spec
python -m source_comfyui check --config secrets/config.json
python -m source_comfyui discover --config secrets/config.json
python -m source_comfyui read --config secrets/config.json --catalog configured_catalog.json
```

## Development

```bash
# Run tests
pytest unit_tests/
pytest integration_tests/  # requires config with real API key

# Run acceptance tests
python -m pytest -p connector_acceptance_test.plugin
```

## Links

- [ComfyUI Cloud API Reference](https://docs.comfy.org/api-reference/cloud)
- [Airbyte Python CDK](https://docs.airbyte.com/platform/connector-development/cdk-python)
- [Airbyte Connector Contribution Guide](https://docs.airbyte.com/community/contributing-to-airbyte)
