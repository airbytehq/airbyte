---
products: enterprise-flex
sidebar_label: Log Collection
---

# Collect Logs from a Flex Data Plane

This guide explains how to collect logs from an Airbyte Flex data plane running in your Kubernetes cluster.

:::info
Requires data plane Helm chart version **2.1.0** or later. Structured JSON logging to stdout is enabled by default starting in 2.1.0. Earlier chart versions emit plaintext logs and do not propagate the log format setting to all containers.
:::

## How Airbyte Emits Logs

The Airbyte data plane has three components that emit logs to stdout:

**Workload Launcher** -- a long-lived Deployment that polls the control plane for work, claims workloads, and launches pods. Emits platform-level logs (queue polling, pod creation, Kubernetes API interactions, errors). Because this is a single pod handling all jobs, it does not carry per-job labels. To find launcher logs for a specific job, search the `message` field for the job ID.

**Orchestrator** -- runs inside each sync workload pod. Aggregates connector logs from the source and destination containers (which can't log to stdout directly -- it's used for Airbyte protocol messages) and emits them alongside its own platform logs. This is the richest log source for debugging sync issues.

**Connector Sidecar** -- runs inside each check/discover/spec workload pod. Emits logs from the connector execution and platform-level logs about the operation.

You collect these logs the same way you collect logs from any other workload in your cluster: with a DaemonSet-based log collector that reads container stdout.

### Log Format

The data plane Helm chart sets `PLATFORM_LOG_FORMAT=json` by default (starting in version 2.1.0). Each line on stdout from all Airbyte containers is a JSON object:

```json
{"timestamp":1740494422000,"message":"Starting sync for connection abc-123","level":"INFO","logSource":"source","caller":{"className":"io.airbyte.container.orchestrator.worker.ReplicationWorker","methodName":"run","lineNumber":245,"threadName":"replication-worker-1"},"throwable":null}
```

| Field | Description |
|---|---|
| `timestamp` | Epoch milliseconds |
| `message` | Log message (secrets and PII are pre-masked) |
| `level` | `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `logSource` | `source`, `destination`, `platform`, or `replication-orchestrator` |
| `caller` | Class, method, line number, and thread name |
| `throwable` | Stack trace (when applicable, otherwise null) |

### Pod Labels

Airbyte workload pods carry labels that your log collector can use for filtering and correlation:

| Label | Description | Present On |
|---|---|---|
| `job_id` | Airbyte job identifier | all pods |
| `attempt_id` | Attempt number for this job | all pods |
| `workspace_id` | Airbyte workspace identifier | all pods |
| `connection_id` | Airbyte connection identifier | sync pods |
| `job_type` | `sync`, `check`, `discover`, `spec` | all pods |
| `source_image_name` | Source connector image (e.g., `source-postgres`) | sync pods |
| `destination_image_name` | Destination connector image (e.g., `destination-bigquery`) | sync pods |
| `actor_type` | Connector actor type | sync, check, discover pods |
| `workload_id` | Internal workload identifier | all pods |

Most log collectors automatically enrich log lines with pod labels as metadata. This lets you filter logs by connection, job, connector, or workspace in your observability stack.

## Setting Up Log Collection

If your cluster does not already have a log collector running, deploy one as a DaemonSet. Below are minimal example configurations for three common collectors. Each is configured to:

- Collect logs from all containers in the cluster
- Parse JSON log lines from Airbyte containers
- Enrich logs with Kubernetes pod labels

Adapt the output/sink section to point at your observability backend.

### Fluent Bit

```bash
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
helm install fluent-bit fluent/fluent-bit \
  --namespace logging --create-namespace \
  --values - <<'EOF'
config:
  inputs: |
    [INPUT]
        Name              tail
        Tag               kube.*
        Path              /var/log/containers/*.log
        multiline.parser  cri
        Mem_Buf_Limit     5MB
        Skip_Long_Lines   On
        Refresh_Interval  5

  filters: |
    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_Tag_Prefix     kube.var.log.containers.
        Merge_Log           On
        Keep_Log            Off
        K8S-Logging.Parser  On
        K8S-Logging.Exclude Off
        Labels              On
        Annotations         Off
        Buffer_Size         256k

  outputs: |
    [OUTPUT]
        Name   stdout
        Match  kube.*
        Format json_lines
EOF
```

> **Important:** The `Buffer_Size 256k` setting on the kubernetes filter is required. Airbyte workload pods have large Kubernetes specs (many environment variables, volume mounts, and secrets). The default buffer size of 32KB is not large enough to hold the Kubernetes API response for pod metadata, which causes label enrichment to silently fail -- log entries will appear without any Kubernetes labels, making them impossible to correlate to specific jobs or connections.

Replace the `[OUTPUT]` section with your backend. Common options:
- `es` (Elasticsearch), `opensearch`, `loki`, `datadog`, `splunk`, `s3`, `forward` (Fluentd)

### Vector

```bash
helm repo add vector https://helm.vector.dev
helm repo update
helm install vector vector/vector \
  --namespace logging --create-namespace \
  --values - <<'EOF'
role: Agent
customConfig:
  sources:
    kubernetes_logs:
      type: kubernetes_logs
      extra_label_selector: "airbyte=job-pod"

  transforms:
    parse_json:
      type: remap
      inputs: ["kubernetes_logs"]
      source: |
        parsed, err = parse_json(.message)
        if err == null {
          . = merge(., parsed)
        }

  sinks:
    stdout:
      type: console
      inputs: ["parse_json"]
      encoding:
        codec: json
EOF
```

Replace the `sinks` section with your backend. Common options:
- `elasticsearch`, `loki`, `datadog_logs`, `splunk_hec`, `aws_cloudwatch_logs`, `gcp_stackdriver_logs`

The `extra_label_selector: "airbyte=job-pod"` filter restricts collection to Airbyte workload pods only (sync, check, discover, spec). Note that the workload-launcher pod does not carry this label, so its logs will not be collected with this filter. Remove the filter to collect from all pods including the workload-launcher.

### Datadog Agent

```bash
helm repo add datadog https://helm.datadoghq.com
helm repo update
helm install datadog datadog/datadog \
  --namespace logging --create-namespace \
  --set datadog.apiKey=<YOUR_API_KEY> \
  --set datadog.logs.enabled=true \
  --set datadog.logs.containerCollectAll=true
```

The Datadog Agent automatically collects container stdout, parses JSON logs, and enriches with Kubernetes labels. No additional configuration is needed beyond providing your API key.

To collect only from Airbyte workload pods, use `datadog.containerExclude` and `datadog.containerInclude` filters, or add pod annotations.

## Verifying Log Collection

After deploying your log collector, trigger a sync from the Airbyte UI and verify logs are flowing:

```bash
# Find the workload pod
kubectl get pods -l airbyte=job-pod --all-namespaces

# Verify the orchestrator container has logs
kubectl logs <pod-name> -c orchestrator -n <namespace>

# Verify pod labels are present
kubectl get pod <pod-name> -n <namespace> --show-labels
```

You should see JSON log lines with `logSource` values of `source`, `destination`, `platform`, and `replication-orchestrator`.

In your observability backend, verify that pod labels (`job_id`, `connection_id`, etc.) appear as metadata on the log entries. If log entries appear but without any Kubernetes labels, the most common cause is the log collector's Kubernetes API buffer being too small -- see the `Buffer_Size` note in the Fluent Bit section above.

## Container Reference

Not all containers in a workload pod have useful logs. In sync pods, the `source` and `destination` containers have empty stdout (it's used for Airbyte protocol messages via named pipes). The `orchestrator` container aggregates all human-readable logs. In check/discover/spec pods, the `sidecar` container has the relevant output. The `init` container in all pod types only emits workload initialization logs.
