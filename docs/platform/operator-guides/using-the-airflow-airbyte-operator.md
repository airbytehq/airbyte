---
description: Trigger Airbyte sync jobs with Apache Airflow
products: all
---

# Using the Airflow Airbyte Provider

Airbyte is an official community provider for the Apache Airflow project. The `apache-airflow-providers-airbyte` package lets you trigger and monitor Airbyte synchronization jobs from Apache Airflow. It works with both Airbyte Cloud and Self-Managed deployments.

The [Airflow Airbyte provider documentation](https://airflow.apache.org/docs/apache-airflow-providers-airbyte/stable/index.html) covers the full API reference and additional configuration options.

## Prerequisites

- An Airbyte instance, either [Cloud](https://cloud.airbyte.com/signup) or [Self-Managed](/platform/using-airbyte/getting-started/oss-quickstart).
- An Apache Airflow instance. If you don't have one, follow the [Airflow quick start guide](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html).
- `apache-airflow-providers-airbyte` version 5.0.0 or later installed in your Airflow environment.

```bash
pip install 'apache-airflow-providers-airbyte>=5.0.0'
```

## Set up the Airflow connection to Airbyte

The Airflow provider authenticates with Airbyte using a Client ID and Client Secret. This is the same authentication method for both Cloud and Self-Managed deployments.

To create your credentials, go to **Settings > Applications** in the Airbyte UI and create a new application. For more details, see [Configuring API Access](/platform/using-airbyte/configuring-api-access).

In the Airflow UI, go to **Admin > Connections** and create a new connection with the connection type **Airbyte**:

- **Connection Id:** A name for this connection, for example `airbyte_default`.
- **Host:** The base URL of the Airbyte API.
  - For Airbyte Cloud: `https://api.airbyte.com/v1/`
  - For Self-Managed: `http://localhost:8000/api/public/v1/`
- **Client ID:** The Client ID from your Airbyte application.
- **Client Secret:** The Client Secret from your Airbyte application.

For more details on connection configuration, see the [Airflow Airbyte connection docs](https://airflow.apache.org/docs/apache-airflow-providers-airbyte/stable/connections.html).

## Retrieve the Airbyte connection ID

Your Airflow DAG needs the Airbyte Connection ID to know which connection to trigger.

1. Open the Airbyte UI.
2. Go to **Connections** and select the connection you want to orchestrate.
3. Copy the connection ID from the URL. The URL format is `https://<domain>/workspaces/<workspace-id>/connections/<connection-id>/status`.

For connections you plan to orchestrate with Airflow, set the sync schedule to **Manual** so Airflow controls when syncs run.

## Create a DAG to trigger an Airbyte sync

### Synchronous example

The following DAG triggers an Airbyte sync and waits for it to complete:

```python
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

with DAG(
    dag_id="trigger_airbyte_sync",
    default_args={"owner": "airflow"},
    schedule_interval="@daily",
    start_date=days_ago(1),
) as dag:

    sync_connection = AirbyteTriggerSyncOperator(
        task_id="sync_airbyte_connection",
        connection_id="your-airbyte-connection-uuid",
        timeout=3600,
        wait_seconds=3,
    )
```

The `AirbyteTriggerSyncOperator` accepts the following parameters:

- `airbyte_conn_id`: The name of the Airflow connection pointing at the Airbyte API. Defaults to `airbyte_default`.
- `connection_id`: The UUID of the Airbyte Connection to trigger.
- `asynchronous`: When `True`, the operator returns the job ID immediately instead of waiting for completion. Default is `False`.
- `timeout`: Maximum seconds to wait for the Airbyte job to complete. Only used when `asynchronous=False`. Default is `3600`.
- `wait_seconds`: Seconds between status checks. Only used when `asynchronous=False`. Default is `3`.

### Asynchronous example

If your Airflow instance has limited resources, use `asynchronous=True` with an `AirbyteJobSensor`. Sensors don't occupy a worker slot, which helps reduce Airflow load.

```python
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.airbyte.sensors.airbyte import AirbyteJobSensor

with DAG(
    dag_id="trigger_airbyte_sync_async",
    default_args={"owner": "airflow"},
    schedule_interval="@daily",
    start_date=days_ago(1),
) as dag:

    trigger_sync = AirbyteTriggerSyncOperator(
        task_id="trigger_airbyte_sync",
        connection_id="your-airbyte-connection-uuid",
        asynchronous=True,
    )

    wait_for_sync = AirbyteJobSensor(
        task_id="wait_for_airbyte_sync",
        airbyte_job_id=trigger_sync.output,
    )

    trigger_sync >> wait_for_sync
```

## Related resources

- [Airflow Airbyte provider documentation](https://airflow.apache.org/docs/apache-airflow-providers-airbyte/stable/index.html)
- [Airflow Airbyte connection configuration](https://airflow.apache.org/docs/apache-airflow-providers-airbyte/stable/connections.html)
- [Configuring Airbyte API access](/platform/using-airbyte/configuring-api-access)
- [Airbyte API reference](https://reference.airbyte.com/reference/start)
