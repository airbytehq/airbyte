# On Kubernetes

## Overview

Airbyte allows scaling sync workloads horizontally using Kubernetes.

## Getting Started

### Cluster Setup
For local testing we recommend following one of the following setup guides:
* [Docker Desktop (Mac)](https://docs.docker.com/desktop/kubernetes/)
* [Minikube](https://minikube.sigs.k8s.io/docs/start/)
  * NOTE: Start Minikube with at least 4gb RAM to Minikube with `minikube start --memory=4000`
* [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)

For testing on GKE you can [create a cluster with the command line or the Cloud Console UI](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster).

For testing on EKS you can [install eksctl](https://eksctl.io/introduction/) and run `eksctl create cluster` to create an EKS cluster/VPC/subnets/etc. This process should take 10-15 minutes.

For production, Airbyte should function on most clusters v1.19 and above. We have tested support on GKE and EKS. If you run into a problem starting Airbyte, please reach out on the `#issues` channel on our [Slack](https://slack.airbyte.io/) or [create an issue on GitHub](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=).

### Install `kubectl`

If you do not already have the CLI tool `kubectl` installed, please follow [these instructions to install](https://kubernetes.io/docs/tasks/tools/).

### Configure `kubectl`

Configure `kubectl` to connect to your cluster by using `kubectl use-context my-cluster-name`.

* For GKE
  * Configure `gcloud` with `gcloud auth login`.
  * On the Google Cloud Console, the cluster page will have a `Connect` button, which will give a command to run locally that looks like `gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE_NAME --project PROJECT_NAME`.
  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl use-context <gke context>` to access the cluster from `kubectl`.
* For EKS
  * [Configure your AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
  * Install [eksctl](https://eksctl.io/introduction/)
  * Run `eksctl utils write-kubeconfig --cluster=<CLUSTER NAME>` to make the context available to `kubectl`
  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl use-context <eks context>` to access the cluster with `kubectl`.

### Launch Airbyte

Run the following commands to launch Airbyte:
```text
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
kubectl apply -k kube/overlays/stable
```

After 2-5 minutes, `kubectl get pods | grep airbyte` should show `Running` as the status for all the core Airbyte pods. This may take longer on Kubernetes clusters with slow internet connections.

Run `kubectl port-forward svc/airbyte-webapp-svc 8000:80` to allow access to the UI/API.

Now visit [http://localhost:8000](http://localhost:8000) in your browser and start moving some data!

## Production Airbyte on Kubernetes

### Cloud logging

TODO

### Using an external DB

After [Issue #3605](https://github.com/airbytehq/airbyte/issues/3605) is completed, users will be able to configure custom dbs instead of a simple `postgres` container running directly in Kubernetes. This separate instance (preferable on a system like AWS RDS or Google Cloud SQL) should be easier and safer to maintain than Postgres on your cluster.

## Known Issues

As we improve our Kubernetes offering, we would like to point out some common pain points. We are working on improving these. Please let us know if there are any other issues blocking your adoption of Airbyte or if you would like to contribute fixes to address any of these issues.

* The server and scheduler deployments must run on the same node. ([#4232](https://github.com/airbytehq/airbyte/issues/4232))
* Some UI operations have higher latency on Kubernetes than Docker-Compose. ([#4233](https://github.com/airbytehq/airbyte/issues/4233))
* Pod histories must be cleaned up manually. ([#3634](https://github.com/airbytehq/airbyte/issues/3634))
* Specifying resource limits for pods is not supported yet. ([#3638](https://github.com/airbytehq/airbyte/issues/3638))
* Pods Airbyte launches to run connector jobs are always launched in the `default` namespace. ([#3636](https://github.com/airbytehq/airbyte/issues/3636))
* File sources reading from and file destinations writing to local mounts are not supported on Kubernetes.

## Customizing Airbyte Manifests

We use [Kustomize](https://kustomize.io/) to allow overrides for different environments. Our shared resources are in the `kube/resources` directory, and we define overlays for each environment. We recommend creating your own overlay if you want to customize your deployments. This overlay can live in your own VCS.

Example `kustomization.yaml` file:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - https://github.com/airbytehq/airbyte.git/kube/overlays/stable?ref=master
```

### View Raw Manifests

For a specific overlay, you can run `kubectl kustomize kube/overlays/stable` to view the manifests that Kustomize will apply to your Kubernetes cluster. This is useful for debugging because it will show the exact resources you are defining.

### Helm Charts
We do not currently offer Helm charts. If you are interested in this functionality please vote on the [related issue](https://github.com/airbytehq/airbyte/issues/1868).

## Operator Guide

### View API Server Logs
`kubectl logs deployments/airbyte-server`

### View Scheduler or Job Logs
`kubectl logs deployments/airbyte-scheduler`

### Connector Container Logs
Although all logs can be accessed by viewing the scheduler logs, connector container logs may be easier to understand when isolated by accessing from the Airbyte UI or the [Airbyte API](../api-documentation.md) for a specific job attempt. Connector pods launched by Airbyte will not relay logs directly to Kubernetes logging. You must access these logs through Airbyte.

### Resizing Volumes

To resize a volume, change the `.spec.resources.requests.storage` value. After re-applying, the mount should be extended if that operation is supported for your type of mount. For a production instance, it's useful to track the usage of volumes to ensure they don't run out of space.

### Copy Files To/From Volumes

See the documentation for [`kubectl cp`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#cp).

### Listing Files

```bash
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx ls /tmp/workspace/8
```

### Reading Files

```bash
kubectl exec -it airbyte-scheduler-6b5747df5c-bj4fx cat /tmp/workspace/8/0/logs.log
```

## Troubleshooting

If you run into any problems operating Airbyte on Kubernetes, please reach out on the `#issues` channel on our [Slack](https://slack.airbyte.io/) or [create an issue on GitHub](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=).

## Developing Airbyte on Kubernetes
[Read about the Kubernetes dev cycle!](https://docs.airbyte.io/contributing-to-airbyte/developing-on-kubernetes)
