# On Kubernetes

## Overview

Airbyte allows scaling sync workloads horizontally using Kubernetes. The core components (api server, scheduler, etc) run as deployments while the scheduler launches connector-related pods on different nodes.

## Getting Started

### Cluster Setup
For local testing we recommend following one of the following setup guides:
* [Docker Desktop (Mac)](https://docs.docker.com/desktop/kubernetes/)
* [Minikube](https://minikube.sigs.k8s.io/docs/start/)
  * NOTE: Start Minikube with at least 4gb RAM to Minikube with `minikube start --memory=4000`
* [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)

For testing on GKE you can [create a cluster with the command line or the Cloud Console UI](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster).

For testing on EKS you can [install eksctl](https://eksctl.io/introduction/) and run `eksctl create cluster` to create an EKS cluster/VPC/subnets/etc. This process should take 10-15 minutes.

For production, Airbyte should function on most clusters v1.19 and above. We have tested support on GKE and EKS. If you run into a problem starting
Airbyte, please reach out on the `#issues` channel on our [Slack](https://slack.airbyte.io/) or [create an issue on GitHub](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=).

### Install `kubectl`

If you do not already have the CLI tool `kubectl` installed, please follow [these instructions to install](https://kubernetes.io/docs/tasks/tools/).

### Configure `kubectl`

Configure `kubectl` to connect to your cluster by using `kubectl use-context my-cluster-name`.

* For GKE
  * Configure `gcloud` with `gcloud auth login`.
  * On the Google Cloud Console, the cluster page will have a `Connect` button, which will give a command to run locally that looks like
    `gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE_NAME --project PROJECT_NAME`.
  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl use-context <gke context>` to access the cluster from `kubectl`.
* For EKS
  * [Configure your AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
  * Install [eksctl](https://eksctl.io/introduction/)
  * Run `eksctl utils write-kubeconfig --cluster=<CLUSTER NAME>` to make the context available to `kubectl`
  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl use-context <eks context>` to access the cluster with `kubectl`.

### Configure Logs

Airbyte requires an S3 bucket for logs. Configure this by filling up the following variables in the `.env` file in the `kube/overlays/stable`
directory:
```text
S3_LOG_BUCKET=
S3_LOG_BUCKET_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

The provided credentials require both S3 read/write permissions. The logger attempts to create the bucket if it does not exist. See [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)
for instructions on creating an S3 bucket and [here](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
for instructions to create AWS credentials.

### Launch Airbyte

Run the following commands to launch Airbyte:
```text
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
kubectl apply -k kube/overlays/stable
```

After 2-5 minutes, `kubectl get pods | grep airbyte` should show `Running` as the status for all the core Airbyte pods. This may take longer
on Kubernetes clusters with slow internet connections.

Run `kubectl port-forward svc/airbyte-webapp-svc 8000:80` to allow access to the UI/API.

Now visit [http://localhost:8000](http://localhost:8000) in your browser and start moving some data!

## Production Airbyte on Kubernetes

### Cloud logging

Airbyte writes logs to two directories. App logs, including server and scheduler logs, are written to the `app-logging` directory.
Job logs are written to the `job-logging` directory. Both directories live at the top-level e.g., the `app-logging` directory lives at
`s3://log-bucket/app-logging` etc. These paths can change, so we recommend having a dedicated log bucket, and to not use this bucket for other
purposes.

Airbyte publishes logs every minute. This means it is normal to see minute-long log delays. Each publish creates it's own log file, since Cloud
Storages do not support append operations. This also mean it is normal to see hundreds of files in your log bucket.

Each log file is named `{yyyyMMddHH24mmss}_{podname}_{UUID}` and is not compressed. Users can view logs simply by navigating to the relevant folder and
downloading the file for the time period in question.

See the [Known Issues](#known-issues) section for planned logging improvements.

### Using an external DB

After [Issue #3605](https://github.com/airbytehq/airbyte/issues/3605) is completed, users will be able to configure custom dbs instead of a simple
`postgres` container running directly in Kubernetes. This separate instance (preferable on a system like AWS RDS or Google Cloud SQL) should be easier
and safer to maintain than Postgres on your cluster.

## Known Issues

As we improve our Kubernetes offering, we would like to point out some common pain points. We are working on improving these. Please let us know if
there are any other issues blocking your adoption of Airbyte or if you would like to contribute fixes to address any of these issues.

* The server and scheduler deployments must run on the same node. ([#4232](https://github.com/airbytehq/airbyte/issues/4232))
* Some UI operations have higher latency on Kubernetes than Docker-Compose. ([#4233](https://github.com/airbytehq/airbyte/issues/4233))
* Pod histories must be cleaned up manually. ([#3634](https://github.com/airbytehq/airbyte/issues/3634))
* Specifying resource limits for pods is not supported yet. ([#3638](https://github.com/airbytehq/airbyte/issues/3638))
* Pods Airbyte launches to run connector jobs are always launched in the `default` namespace. ([#3636](https://github.com/airbytehq/airbyte/issues/3636))
* S3 is the only Cloud Storage currently supported. ([#4200](https://github.com/airbytehq/airbyte/issues/4200))
* Large log files might take a while to load. ([#4201](https://github.com/airbytehq/airbyte/issues/4201))
* UI does not include configured buckets in the displayed log path. ([#4204](https://github.com/airbytehq/airbyte/issues/4204))
* Logs are not reset when Airbyte is re-deployed. ([#4235](https://github.com/airbytehq/airbyte/issues/4235))
* File sources reading from and file destinations writing to local mounts are not supported on Kubernetes.

## Customizing Airbyte Manifests

We use [Kustomize](https://kustomize.io/) to allow overrides for different environments. Our shared resources are in the `kube/resources` directory,
and we define overlays for each environment. We recommend creating your own overlay if you want to customize your deployments.
This overlay can live in your own VCS.

Example `kustomization.yaml` file:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - https://github.com/airbytehq/airbyte.git/kube/overlays/stable?ref=master
```

### View Raw Manifests

For a specific overlay, you can run `kubectl kustomize kube/overlays/stable` to view the manifests that Kustomize will apply to your Kubernetes cluster.
This is useful for debugging because it will show the exact resources you are defining.

### Helm Charts
We do not currently offer Helm charts. If you are interested in this functionality please vote on the [related issue](https://github.com/airbytehq/airbyte/issues/1868).

## Operator Guide

### View API Server Logs
`kubectl logs deployments/airbyte-server` to view real-time logs. Logs can also be downloaded as a text file via the Admin tab in the UI. 

### View Scheduler or Job Logs
`kubectl logs deployments/airbyte-scheduler` to view real-time logs. Logs can also be downloaded as a text file via the Admin tab in the UI.

### Connector Container Logs
Although all logs can be accessed by viewing the scheduler logs, connector container logs may be easier to understand when isolated by accessing from
the Airbyte UI or the [Airbyte API](../api-documentation.md) for a specific job attempt. Connector pods launched by Airbyte will not relay logs directly
to Kubernetes logging. You must access these logs through Airbyte.

### Upgrading Airbyte Kube
See [Upgrading K8s](../operator-guides/upgrading-airbyte.md).

### Resizing Volumes
To resize a volume, change the `.spec.resources.requests.storage` value. After re-applying, the mount should be extended if that operation is supported
for your type of mount. For a production instance, it's useful to track the usage of volumes to ensure they don't run out of space.

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
If you run into any problems operating Airbyte on Kubernetes, please reach out on the `#issues` channel on our [Slack](https://slack.airbyte.io/) or
[create an issue on GitHub](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=).

## Developing Airbyte on Kubernetes
[Read about the Kubernetes dev cycle!](https://docs.airbyte.io/contributing-to-airbyte/developing-on-kubernetes)
