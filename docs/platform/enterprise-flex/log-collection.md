---
products: enterprise-flex
sidebar_label: Logs
---

# Logs from a Flex Data Plane

This guide explains where the logs from an Airbyte Flex data plane go, how to view sync logs in Airbyte's user interface, and how to collect logs from your Kubernetes cluster into your own observability stack.

These logs describe the work your data plane does: sync, check, discover, and spec jobs. To review who changed your Airbyte configuration, see [Audit logs](/platform/access-management/audit-logs) instead.

## Choose where your logs go

In Enterprise Flex, the control plane Airbyte manages never has direct access to your cluster. That means Airbyte can't show you job logs in the user interface unless your data plane sends those logs to Airbyte. You have two options, and you can use both at the same time.

| Option | Where logs are stored | Who can see them | How to set it up |
| --- | --- | --- | --- |
| [View job logs in Airbyte](#airbyte-ui) | Airbyte-managed storage in the control plane | You, in Airbyte's UI and API. Airbyte's support team, when you ask for help. | Contact Airbyte support to enable it for your organization. Off by default. |
| [Keep logs in your own infrastructure](#own-infrastructure) | Your object storage bucket, your observability backend, or both | Only you. Airbyte can't see them. | Configure a `storage` bucket in your data plane's `values.yaml`, run a log collector in your cluster, or both. |

Whichever option you choose, logging never causes a job to fail. If the data plane can't deliver a job's logs, the job continues and only the logs are affected.

:::info Which logs this affects
This choice controls the logs for sync, check, and discover jobs. Spec jobs and the workload launcher always log only to your cluster.
:::

## View job logs in Airbyte {#airbyte-ui}

When Airbyte enables this option for your organization, workloads in your data plane upload their job logs to storage that Airbyte manages. You then see logs for syncs, connection tests (check), and schema discovery in Airbyte's user interface and API exactly as you would for a Cloud data plane.

### Why you might want this

- You can troubleshoot syncs from the Airbyte UI without going to your cluster or your observability tool.
- Airbyte's support team can investigate issues directly. Support cases resolve faster when Airbyte can see the logs.

### Why you might not want this

Job logs leave your environment and are stored in Airbyte's control plane. Logs don't contain the records you sync, and Airbyte masks secrets and personally identifiable information before writing them, but connector log lines can still reveal information you consider sensitive, like table names, hostnames, query text, or error messages that quote data. If you chose Enterprise Flex to keep all workload output inside your infrastructure or a specific region, you may prefer to keep logs in your own infrastructure instead. You can still work with Airbyte support in that case. See [Support without logs in Airbyte](#support).

### How it works

- Airbyte enables this option per organization, on request. It's off by default, and it never turns on without you asking for it.
- Your data plane authenticates to Airbyte's control plane as usual. For each eligible job, the control plane issues the workload a short-lived credential that can only create objects under that job's own path in Airbyte's log storage. The credential can't read, list, or delete anything, and it can't touch other jobs' logs.
- The workload uploads its logs directly to Airbyte's log storage. Log data doesn't pass through the control plane's API, and the credential is held only in memory by the orchestrator or sidecar container, never in your connector containers.
- If the workload can't get a credential or can't upload, it falls back to logging the way it did before, and the job continues.
- You don't add any storage credentials or Helm values for this option. Airbyte turns it on for you.

### Request or disable it

To turn this option on or off, [contact Airbyte support](https://support.airbyte.com/) and tell them the organization you want to change. After Airbyte enables it, run a sync and open its logs in the Airbyte UI to confirm they load. To turn it off, contact support again. Jobs that start after Airbyte turns it off log only to your cluster.

:::note
Your data plane needs Helm chart version **2.3.0** or later for this option. Upgrade your data plane before you ask Airbyte to enable it.
:::

## Keep logs in your own infrastructure {#own-infrastructure}

If you don't enable Airbyte-hosted logs, your job logs stay in your cluster. You have two ways to keep them.

**Store job logs in your own bucket.** Set the `storage` section in your data plane's `values.yaml` to an S3, GCS, or Azure Blob Storage bucket, as shown in [Deploy a data plane](data-plane#step-4). The orchestrator and sidecar write each job's logs to `job-logging/` in the `storage.bucket.log` bucket. If you don't configure `storage`, the data plane has nowhere to write job logs and silently discards them after each job. The logs are still on the containers' stdout while the pod runs, so a log collector can still capture them.

**Collect container stdout.** Run a log collector in your cluster and ship logs to your own observability backend. The rest of this guide explains how.

### Support without logs in Airbyte {#support}

If your logs stay in your infrastructure, Airbyte's support team can't see them. When you open a support case, Airbyte may ask you to share the relevant logs. Have them ready:

- If you store job logs in your own bucket, download the objects under `job-logging/` for the affected job and attempt.
- If you collect stdout, export the log entries for the affected job. Filter on the `job_id`, `attempt_id`, or `connection_id` [pod labels](#pod-labels).
- If you do neither, run `kubectl logs` on the workload pod's `orchestrator` or `sidecar` container while it's running. See [Container reference](#container-reference).

:::info
Collecting stdout requires data plane Helm chart version **2.1.0** or later. Structured JSON logging to stdout is enabled by default starting in 2.1.0. Earlier chart versions emit plaintext logs and do not propagate the log format setting to all containers.
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

### Pod Labels {#pod-labels}

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

## Container Reference {#container-reference}

Not all containers in a workload pod have useful logs. In sync pods, the `source` and `destination` containers have empty stdout (it's used for Airbyte protocol messages via named pipes). The `orchestrator` container aggregates all human-readable logs. In check/discover/spec pods, the `sidecar` container has the relevant output. The `init` container in all pod types only emits workload initialization logs.
