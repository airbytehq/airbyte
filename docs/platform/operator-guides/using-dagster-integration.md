---
description: Trigger Airbyte sync jobs with Dagster
products: all
---

# Using the Dagster Integration

Airbyte is an official integration in the Dagster project. The `dagster-airbyte` package lets you represent Airbyte connections as Dagster assets and trigger synchronization jobs. It works with both Airbyte Cloud and Self-Managed deployments.

The [dagster-airbyte API documentation](https://docs.dagster.io/api/libraries/dagster-airbyte) covers the full API reference.

## Prerequisites

- An Airbyte instance, either [Cloud](https://cloud.airbyte.com/signup) or [Self-Managed](/platform/using-airbyte/getting-started/oss-quickstart).
- A Dagster instance. If you don't have one, follow the [Dagster getting started guide](https://docs.dagster.io/getting-started).
- `dagster-airbyte` installed in your Dagster environment.

```bash
pip install dagster-airbyte
```

## Airbyte Cloud

Use `AirbyteCloudWorkspace` to connect Dagster to Airbyte Cloud.

### Create API credentials

Go to **Settings > Applications** in the Airbyte Cloud UI and create a new application to get a Client ID and Client Secret. For more details, see [Configuring API Access](/platform/using-airbyte/configuring-api-access).

### Define the workspace resource and load assets

```python
from dagster_airbyte import AirbyteCloudWorkspace, build_airbyte_assets_definitions
import dagster as dg

airbyte_workspace = AirbyteCloudWorkspace(
    workspace_id=dg.EnvVar("AIRBYTE_WORKSPACE_ID"),
    client_id=dg.EnvVar("AIRBYTE_CLIENT_ID"),
    client_secret=dg.EnvVar("AIRBYTE_CLIENT_SECRET"),
)

airbyte_assets = build_airbyte_assets_definitions(workspace=airbyte_workspace)

defs = dg.Definitions(
    assets=airbyte_assets,
    resources={"airbyte": airbyte_workspace},
)
```

## Self-Managed (OSS)

Use `AirbyteWorkspace` to connect Dagster to a Self-Managed Airbyte instance.

### Create API credentials

Go to **Settings > Applications** in the Airbyte UI and create a new application. For more details, see [Configuring API Access](/platform/using-airbyte/configuring-api-access).

### Define the workspace resource and load assets

```python
from dagster_airbyte import AirbyteWorkspace, build_airbyte_assets_definitions
import dagster as dg

airbyte_workspace = AirbyteWorkspace(
    rest_api_base_url="http://localhost:8000/api/public/v1",
    configuration_api_base_url="http://localhost:8000/api/v1",
    workspace_id=dg.EnvVar("AIRBYTE_WORKSPACE_ID"),
    client_id=dg.EnvVar("AIRBYTE_CLIENT_ID"),
    client_secret=dg.EnvVar("AIRBYTE_CLIENT_SECRET"),
)

airbyte_assets = build_airbyte_assets_definitions(workspace=airbyte_workspace)

defs = dg.Definitions(
    assets=airbyte_assets,
    resources={"airbyte": airbyte_workspace},
)
```

## Triggering syncs

Once your Airbyte assets are loaded, Dagster can materialize them to trigger syncs. You can trigger syncs through the Dagster UI by materializing the corresponding assets, or programmatically by including them in a Dagster job.

For connections you plan to orchestrate with Dagster, set the Airbyte sync schedule to **Manual** so Dagster controls when syncs run.

## Migrating from the legacy API

If you are using the older `airbyte_resource` and `airbyte_sync_op` patterns, Dagster recommends migrating to the workspace-based API described above. The legacy API only supports Self-Managed deployments and does not integrate with Dagster's asset framework.

See the [dagster-airbyte migration guide](https://docs.dagster.io/integrations/libraries/airbyte/) for details on updating your code.

## Related resources

- [dagster-airbyte API reference](https://docs.dagster.io/api/libraries/dagster-airbyte)
- [Dagster Airbyte integration guide](https://docs.dagster.io/integrations/libraries/airbyte/)
- [Configuring Airbyte API access](/platform/using-airbyte/configuring-api-access)
- [Airbyte API reference](https://reference.airbyte.com/reference/start)
