---
products: all
---

# Monitoring Airbyte

Airbyte offers extensive logging capabilities.

## Connection logging

All Airbyte instances include extensive logging for each connector. These logs give you detailed reports on each data sync. [Learn more about browsing logs](browsing-output-logs).

## Datadog Integration

Airbyte uses Datadog to monitor Airbyte Cloud performance on a [number of metrics](https://docs.datadoghq.com/integrations/airbyte/#data-collected) important to your experience. This integration only works on legacy Docker deployments of Airbyte. We're working on an improved version for abctl and Kubernetes. This could become available later as an enterprise feature to help you monitor your own deployment. If you're an enterprise customer and Datadog integration is important to you, let us know.

![Datadog's Airbyte Integration Dashboard](assets/DatadogAirbyteIntegration_OutOfTheBox_Dashboard.png)

## OpenTelemetry metrics monitoring (Self-Managed Enterprise only) {#otel}

Airbyte Self-Managed Enterprise generates a number of crucial metrics about syncs and volumes of data moved. You can configure Airbyte to send telemetry data to an OpenTelemetry collector endpoint so you can consume these metrics in your downstream monitoring tool of choice. Airbyte does not send traces and logs.

Airbyte sends specific metrics to provide you with health insight in the following areas.

- Resource provisioning: Monitor API requests and sync attempts to ensure your deployment has adequate resources

- Sync performance: Track sync duration and data volume moved to understand performance

- System health: Monitor sync status and completion rates to ensure system stability

### Configure OpenTelemetry metrics

1. Deploy an OpenTelemetry collector if you don't already have one. See the [OpenTelemetry documentation](https://opentelemetry.io/docs/collector/getting-started/#kubernetes) for help doing this. If you use Datadog as your monitoring tool, they have an excellent guide to [set up a collector and exporter](https://docs.datadoghq.com/opentelemetry/collector_exporter/).

2. Update your `values.yaml` file to enable OpenTelemetry.

    ```yaml
    global:
        edition: enterprise # This is an enterprise-only feature
        metrics:
            enabled: true
            otlp:
                enabled: true
                collectorEndpoint: "YOUR_ENDPOINT" # The OTel collector endpoint Airbyte sends metrics to. You configure this endpoint outside of Airbyte as part of your OTel deployment.
    ```

3. Redeploy Airbyte with the updated values.

Airbyte sends metrics to the collector you specified in your configuration.

### Available metrics

The following metrics are available. They're published every minute.

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Tag</th>
      <th>Example Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="8"><code>airbyte.syncs</code></td>
      <td><code>connection_id</code></td>
      <td>653a067e-cd0b-4cab-96b5-5e5cb03f159b</td>
    </tr>
    <tr>
      <td><code>workspace_id</code></td>
      <td>bed3b473-1518-4461-a37f-730ea3d3a848</td>
    </tr>
    <tr>
      <td><code>job_id</code></td>
      <td>23642492</td>
    </tr>
    <tr>
      <td><code>status</code></td>
      <td>success, failed</td>
    </tr>
    <tr>
      <td><code>attempt_count</code></td>
      <td>3</td>
    </tr>
    <tr>
      <td><code>version</code></td>
      <td>1.5.0</td>
    </tr>
    <tr>
      <td><code>source_connector_id</code></td>
      <td>82c7fb2d-7de1-4d4e-b12e-510b0d61e374</td>
    </tr>
    <tr>
      <td><code>destination_connector_id</code></td>
      <td>3cb42982-755b-4644-9ed4-19651b53ebdd</td>
    </tr>
    <tr>
      <td rowspan="6"><code>airbyte.gb_moved</code></td>
      <td><code>connection_id</code></td>
      <td>653a067e-cd0b-4cab-96b5-5e5cb03f159b</td>
    </tr>
    <tr>
      <td><code>workspace_id</code></td>
      <td>bed3b473-1518-4461-a37f-730ea3d3a848</td>
    </tr>
    <tr>
      <td><code>job_id</code></td>
      <td>23642492</td>
    </tr>
    <tr>
      <td><code>source_connector_id</code></td>
      <td>82c7fb2d-7de1-4d4e-b12e-510b0d61e374</td>
    </tr>
    <tr>
      <td><code>destination_connector_id</code></td>
      <td>3cb42982-755b-4644-9ed4-19651b53ebdd</td>
    </tr>
    <tr>
      <td><code>version</code></td>
      <td>1.5.0</td>
    </tr>
    <tr>
      <td rowspan="6"><code>airbyte.sync_duration</code></td>
      <td><code>connection_id</code></td>
      <td>653a067e-cd0b-4cab-96b5-5e5cb03f159b</td>
    </tr>
    <tr>
      <td><code>workspace_id</code></td>
      <td>bed3b473-1518-4461-a37f-730ea3d3a848</td>
    </tr>
    <tr>
      <td><code>job_id</code></td>
      <td>23642492</td>
    </tr>
    <tr>
      <td><code>source_connector_id</code></td>
      <td>82c7fb2d-7de1-4d4e-b12e-510b0d61e374</td>
    </tr>
    <tr>
      <td><code>destination_connector_id</code></td>
      <td>3cb42982-755b-4644-9ed4-19651b53ebdd</td>
    </tr>
    <tr>
      <td><code>version</code></td>
      <td>1.5.0</td>
    </tr>
    <tr>
      <td rowspan="3"><code>airbyte.api_requests</code></td>
      <td><code>workspace_id</code></td>
      <td>bed3b473-1518-4461-a37f-730ea3d3a848</td>
    </tr>
    <tr>
      <td><code>endpoint</code></td>
      <td>/v1/connections/sync</td>
    </tr>
    <tr>
      <td><code>status</code></td>
      <td>200</td>
    </tr>
  </tbody>
</table>
