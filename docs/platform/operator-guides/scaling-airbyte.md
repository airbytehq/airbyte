---
products: enterprise-flex
---

# Scaling Airbyte

Airbyte's scalable self-managed option is [Enterprise Flex](../enterprise-flex/readme.md). Airbyte runs the control plane for you in Airbyte Cloud, and you run one or more data planes in your own infrastructure. Scaling Airbyte means scaling those data planes: giving them enough compute, running enough of them in the right places, and tuning how many jobs they run at once.

This guide explains what to scale and how. It assumes you already have a data plane running. If you don't, see [Deploy a data plane with Helm](../enterprise-flex/data-plane.md).

## Open source isn't a scalable deployment

Airbyte Core, the open source version of Airbyte, is a single-user tool for evaluating Airbyte and running small workloads. It isn't designed to run at scale and Airbyte doesn't support tuning its control plane components. It lacks the capabilities a scaled, shared deployment needs.

- No user accounts, [SSO](../access-management/sso.md), [role-based access control](../access-management/rbac.md), [SCIM](../access-management/scim.md), or other governance features.
- No multiple regions or multiple data planes. The control plane and workers run together on one cluster.
- No capacity controls, so there's no way to guarantee critical syncs run when the cluster is busy.

If you're running Core and outgrowing it, move to [Enterprise Flex](../enterprise-flex/readme.md) or [Airbyte Cloud](https://airbyte.com/product/airbyte-cloud) rather than trying to scale Core.

:::note
[Airbox](../enterprise-flex/data-plane-util.md) deploys a data plane onto a single machine with Docker Desktop. It's a fast way to start moving data, not a scaled deployment. For production workloads, deploy data planes to a Kubernetes cluster with Helm.
:::

## What to scale

[Workloads](../understanding-airbyte/jobs.md) do the heavy lifting in Airbyte. For every job (sync, check, discover), the data plane's workload launcher starts a Kubernetes pod that runs the connector and sidecar containers. The control plane orchestrates jobs but doesn't move data.

Scaling a data plane comes down to a few dimensions.

| Dimension                   | What it controls                                                     |
| --------------------------- | -------------------------------------------------------------------- |
| Cluster size                | How many job pods can be scheduled at once and how large they can be |
| Number of data planes       | Where jobs run, and how resilient each region is                     |
| Concurrency                 | How many jobs a data plane launches at once                          |
| Pod resources               | CPU and memory available to each connector                           |
| Node pools and auto-scaling | Which nodes job pods land on and whether the cluster grows with load |

## Size your cluster

Airbyte recommends deploying to Amazon EKS, Google Kubernetes Engine, or Azure Kubernetes Service across 2 or more availability zones. See [Infrastructure prerequisites](../enterprise-flex/data-plane.md#infrastructure-prerequisites) for supported platforms.

Each sync runs as one pod with three containers: the source, the destination, and an orchestrator that moves data between them. Checks and schema discovery run in their own short-lived pods. As a rule of thumb, make sure the cluster can schedule at least `<maximum concurrent syncs>` sync pods at once, plus headroom for check and discover pods.

Start with a mid-sized cluster (for example, nodes with 4 or 8 cores) and tune from there based on the usage you observe. Connector images are around 300 MB each, and long-running syncs produce logs, so allocate at least 30 GB of disk per node.

## Run multiple data planes

A data plane belongs to a region, and each workspace runs its connections in one region. Add data planes when you need to:

- **Run in more places.** Create a region and a data plane for each geography or cloud where data must stay, then assign workspaces to those regions. See [Determine which regions you need](../enterprise-flex/getting-started.md#determine-which-regions-you-need).
- **Add availability within a region.** Run two or more data planes in the same region. Both must belong to the same Airbyte region and use the same secrets manager. See [Limitations and considerations](../enterprise-flex/getting-started.md#limitations-and-considerations).

Data planes only make outbound requests to the control plane, so adding a data plane doesn't require new inbound network rules. Each data plane must use the same secrets manager as the control plane.

## Control concurrency

Two settings determine how many jobs run at once.

- **Data workers.** Your organization has a contracted number of data workers, allocated per region. When a region's data workers are all in use, new syncs in that region queue until capacity is available. You can move capacity between regions and enable on-demand capacity for critical connections. See [Manage and monitor data workers](../cloud/managing-airbyte-cloud/manage-data-workers.md).
- **Launcher parallelism.** Each data plane's workload launcher claims and starts up to `workloadLauncher.parallelism` jobs at once (default: 10). This limits how many jobs one launcher replica is starting concurrently, not how many can run. Raise it in your data plane's Helm values if jobs are waiting to start while the cluster still has room. To scale the launcher horizontally or make it resilient, raise `workloadLauncher.replicaCount`; replicas share the claim queue.

Concurrency only helps if the cluster has room for the resulting pods. Raise launcher parallelism and cluster capacity together.

## Set pod resources

Connector pods request CPU and memory from the cluster. Too little and syncs slow down or fail with out-of-memory errors. Too much and the cluster runs fewer pods than it could.

By default, Airbyte applies per-connector resource defaults that it maintains (`workloads.resources.useConnectorResourceDefaults: true`). Set your own data plane-wide defaults for connector containers in your Helm values under `workloads.resources.mainContainer`, and tune the other containers under `workloads.resources.check`, `workloads.resources.discover`, `workloads.resources.replication` (the orchestrator container in sync pods), and `workloads.resources.sidecar`. Each takes `cpu` and `memory` with `request` and `limit` keys. To override resources for one connector type or one connection, see [Configuring connector resources](configuring-connector-resources.md).

Memory is the most common constraint. The orchestrator buffers records between the source and destination, so database tables with large rows or wide schemas need more memory than the defaults provide. For how Kubernetes applies requests and limits, see [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/).

## Use node pools and auto-scaling

Job pods are short-lived and spiky, which makes them a good fit for a dedicated node pool that scales automatically.

- Use `jobs.kube.nodeSelector` and `jobs.kube.tolerations` in your Helm values to place job pods on a node pool that's separate from the data plane's long-running services.
- Enable [node auto-scaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/) for that node pool in your cloud provider so nodes are added when pods are pending and removed when they finish. Set the pool's maximum size high enough to hold your peak number of concurrent sync pods.
- Keep pod resource requests accurate. Kubernetes adds and removes nodes based on pod requests, not actual usage. Requests that are too low cause pods to be scheduled onto nodes that can't sustain them; requests that are too high leave nodes underused.

## Monitor and adjust

Use the data worker [usage chart](../cloud/managing-airbyte-cloud/manage-data-workers.md#how-to-interpret-the-usage-chart) to see peak concurrency per region, and your cluster's metrics to see whether pods are pending, evicted, or hitting memory limits. Adjust one dimension at a time and watch the effect before changing the next.
