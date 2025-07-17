---
products: oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Scaling Airbyte After Installation

Once you've completed the initial installation of Airbyte Self-Managed Enterprise, the next crucial step is scaling your setup as needed to ensure optimal performance and reliability as your data integration needs grow. This guide will walk you through best practices and strategies for scaling Airbyte in an enterprise environment.

## Concurrent Syncs

The primary driver of increased resource usage in Airbyte is the number of concurrent syncs running at any given time. Each concurrent sync requires at least 3 additional connector pods to be running at once (`orchestrator`, `read`, `write`). For example, 10 concurrent syncs require 30 additional pods in your namespace. Connector pods last only for the duration of a sync, and will be appended by the ID of the ongoing job.

If your deployment of Airbyte is intended to run many concurrent syncs at once (e.g. an overnight backfill), you are likely to require an increased number of instances to run all syncs. 

### Connector CPU & Memory Settings

Some connectors are memory and CPU intensive, while others are not. Using an infrastructure monitoring tool, we recommend measuring the following at all times:
* Requested CPU %
* CPU Usage %
* Requested Memory %
* Memory Usage %

If your nodes are under high CPU or Memory usage, we recommend scaling up your Airbyte deployment to a larger number of nodes, or reducing the maximum resource usage by any given connector pod. If high _requested_ CPU or memory usage is blocking new pods from being scheduled, while _used_ CPU or memory is low, you may modify connector pod provisioning defaults in your `values.yaml` file:

```yaml title="values.yaml"
global:
  edition: "enterprise"
  # ...
  jobs:
    resources:
      limits:
        cpu: ## e.g. 250m
        memory: ## e.g. 500m
      requests:
        cpu: ## e.g. 75m
        memory: ## e.g. 150m
```

If your Airbyte deployment is under-provisioned, you may notice occasional 'stuck jobs' that remain in-progress for long periods, with eventual failures related to unavailable pods. Increasing job CPU and memory limits may also allow for increased sync speeds. For help and best practices, see [Configuring connector resources](../operator-guides/configuring-connector-resources).

### Concurrent Sync Limits

To help rightsize Airbyte deployments and reduce the likelihood of stuck syncs, there are configurable limits to the number of syncs that can be run at once:

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
worker:
  extraEnv: ## We recommend setting both environment variables with a single, shared value.
    - name: MAX_SYNC_WORKERS
      value: ## e.g. 5
    - name: MAX_CHECK_WORKERS
      value: ## e.g. 5
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
worker:
  maxSyncWorkers: ## e.g. 5
  maxCheckWorkers: ## e.g. 5
```

</TabItem>
</Tabs>

If you intend to run many syncs at the same time, you may also want to increase the number of worker replicas that run in your Airbyte instance:

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
worker:
  replicaCount: ## e.g. 2
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
worker:
  replicaCount: ## e.g. 2
```

</TabItem>
</Tabs>

## Multiple Node Groups

To reduce the blast radius of an underprovisioned Airbyte deployment, place 'static' workloads (`webapp`, `server`, etc.) on one Kubernetes node group, while placing job-related workloads (connector pods) on a different Kubernetes node group. This ensures that UI or API availability is unlikely to be impacted by the number of concurrent syncs.

<details>
<summary>Configure Airbyte Self-Managed Enterprise to run in two node groups</summary>

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
airbyte-bootloader:
  nodeSelector:
    type: static

server:
  nodeSelector:
    type: static

keycloak:
  nodeSelector:
    type: static

keycloak-setup:
  nodeSelector:
    type: static

temporal:
  nodeSelector:
    type: static

webapp:
  nodeSelector:
    type: static

worker:
  nodeSelector:
    type: jobs

workload-launcher:
  nodeSelector:
    type: static
  ## Pods spun up by the workload launcher will run in the 'jobs' node group.
  extraEnv:
    - name: JOB_KUBE_NODE_SELECTORS
      value: type=jobs
    - name: SPEC_JOB_KUBE_NODE_SELECTORS
      value: type=jobs
    - name: CHECK_JOB_KUBE_NODE_SELECTORS
      value: type=jobs
    - name: DISCOVER_JOB_KUBE_NODE_SELECTORS
      value: type=jobs

orchestrator:
  nodeSelector:
    type: jobs
  
workload-api-server:
  nodeSelector:
    type: jobs
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
global:
  jobs:
    kube:
      nodeSelector:
        type: jobs
      scheduling:
        check:
          nodeSelectors:
            type: jobs
        discover:
          nodeSelectors:
            type: jobs
        spec:
          nodeSelectors:
            type: jobs
            
airbyteBootloader:
  nodeSelector:
    type: static

server:
  nodeSelector:
    type: static

keycloak:
  nodeSelector:
    type: static

keycloakSetup:
  nodeSelector:
    type: static

temporal:
  nodeSelector:
    type: static

webapp:
  nodeSelector:
    type: static

workloadLauncher:
  nodeSelector:
    type: static

worker:
  nodeSelector:
    type: jobs
  
workloadApiServer:
  nodeSelector:
    type: jobs
```

</TabItem>
</Tabs>

</details>

## High Availability

You may wish to implement high availability (HA) to minimize downtime and ensure continuous data integration processes. Please note that this requires provisioning Airbyte on a larger number of Nodes, which may increase your licensing fees. For a typical HA deployment, you will want a VPC with subnets in at least two (and preferably three) availability zones (AZs).

We particularly recommend having multiple instances of `worker` and `server` pods:

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
worker:
  replicaCount: 2

server:
  replicaCount: 2
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
worker:
  replicaCount: 2

server:
  replicaCount: 2
```

</TabItem>
</Tabs>

Furthermore, you may want to implement a primary-replica setup for the database (e.g., PostgreSQL) used by Airbyte. The primary database handles write operations, while replicas handle read operations, ensuring data availability even if the primary fails.

## Disaster Recovery (DR) Regions

For business-critical applications of Airbyte, you may want to configure a Disaster Recovery (DR) cluster for Airbyte. We do not support assisting customers with DR deployments at this time. However, we offer a few high level suggestions:

1. We strongly recommend configuring an external database, external log storage and external connector secret management.

2. We strongly recommend that your DR cluster is also an instance of Self-Managed Enterprise, kept at the same version as your prod instance.

## DEBUG Logs

We recommend turning off `DEBUG` logs for any non-testing use of Self-Managed Airbyte. Failing to do while running at-scale syncs may result in the `server` pod being overloaded, preventing most of the deployment for operating as normal.

## Schema Discovery Timeouts 

While configuring a database source connector with hundreds to thousands of tables, each with many columns, the one-time `discover` mechanism - by which we discover the topology of your source - may run for a long time and exceed Airbyte's timeout duration. Should this be the case, you may increase Airbyte's timeout limit as follows:

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
server:
  extraEnv:
    - name: HTTP_IDLE_TIMEOUT
      value: 20m
    - name: READ_TIMEOUT
      value: 30m
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
server:
  httpIdleTimeout: 20m
  extraEnv:
    - name: READ_TIMEOUT
      value: 30m
```

</TabItem>
</Tabs>
