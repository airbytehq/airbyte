# Collecting Metrics

Airbyte supports two ways to collect metrics - using datadog or open telemetry. 
Fill in `METRIC_CLIENT` field in `.env` file to get started!

# Open Telemetry

1. In `.env` change `METRIC_CLIENT` to `otel`. 
2. Similarly, configure `OTEL_COLLECTOR_ENDPOINT` to tell Airbyte where to send metrics RPC to.

## Example

### Run Opentelemetry and Airbyte locally

In this example we will run Airbyte locally along with an Open Telemetry Collector. The Open telemetry collector
will expose port 4317 to the localhost as the receiving endpoint.

![](../.gitbook/assets/open_telemetry_example.png)

Steps:

1. Setting up Open telemetry. In this example we will use the repository from `opentelemetry-java-docs`. 
Run the following commands to have it up and running.

```bash
  git clone https://github.com/open-telemetry/opentelemetry-java-docs
  cd opentelemetry-java-docs/otlp/docker
  docker-compose up
```

2. Configure Airbyte `.env` file. 
   1. Change `METRIC_CLIENT` to `otel` to indicate Airbyte to use Open telemetry to emit metric data.
   2. Change `OTEL_COLLECTOR_ENDPOINT` to `"http://host.docker.internal:4317"` because Open Telemetry 
   Collector has enabled port forward from localhost:4317 to container port 4317. To send data to Collector container port 4317, we want to need to export data to physical machine's localhost:4317, which in docker will be represented as `http://host.docker.internal:4317`. 
   > Do *not* use `localhost:4317` or you will send data to the same container where Airbyte Worker is running.
   3. Start Airbyte server by running `docker-compose up` under airbyte repository. Go to `localhost:8000` to visit Airbyte and start a sync, then go to `localhost:9090` to access Prometheus - you should be able to see the metrics there. Alternatively, 

### Run Opentelemetry and Airbyte on kubernetes

> **Prerequisite:** Read https://github.com/airbytehq/airbyte/blob/master/docs/deploying-airbyte/on-kubernetes.md to understand how to start Airbyte on Kubernetes

We will use `stable` in this example.

Steps:
1. Run open telemetry collector in the same Kubernetes context. Here we follow example in [OpenTelemetry doc](https://opentelemetry.io/docs/collector/getting-started/#kubernetes)
2. edit `kube/overlays/stable/.env` and add the following lines:

```aidl
METRIC_CLIENT=otel
OTEL_COLLECTOR_ENDPOINT=<address>
```

If you started open telemetry collector in the link above, the address should be `http://otel-collector:4317`. 
Note the format - unlike the base `.env`, there is no quote in `.env` file under kubernetes.

# Datadog
TBD

## Metrics
Visit [OssMetricsRegistry.java](https://github.com/airbytehq/airbyte/blob/master/airbyte-metrics/metrics-lib/src/main/java/io/airbyte/metrics/lib/OssMetricsRegistry.java) to get a complete list of metrics Airbyte is sending.

