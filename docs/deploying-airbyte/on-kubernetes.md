# On Kubernetes (Beta)

## Overview

Airbyte allows scaling sync workloads horizontally using Kubernetes. The core components \(api server, scheduler, etc\) run as deployments while the scheduler launches connector-related pods on different nodes.

## Quickstart

If you don't want to configure your own K8s cluster and Airbyte instance, you can use the free, open-source project [Plural](https://www.plural.sh/) to bring up a K8s cluster and Airbyte for you. Use [this guide](on-plural.md) to get started.

## Getting Started

### Cluster Setup

For local testing we recommend following one of the following setup guides:

* [Docker Desktop \(Mac\)](https://docs.docker.com/desktop/kubernetes)
* [Minikube](https://minikube.sigs.k8s.io/docs/start)
  * NOTE: Start Minikube with at least 4gb RAM with `minikube start --memory=4000`
* [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)

For testing on GKE you can [create a cluster with the command line or the Cloud Console UI](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster).

For testing on EKS you can [install eksctl](https://eksctl.io/introduction/) and run `eksctl create cluster` to create an EKS cluster/VPC/subnets/etc. This process should take 10-15 minutes.

For production, Airbyte should function on most clusters v1.19 and above. We have tested support on GKE and EKS. If you run into a problem starting Airbyte, please reach out on the `#troubleshooting` channel on our [Slack](https://slack.airbyte.io/) or [create an issue on GitHub](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=).

### Install `kubectl`

If you do not already have the CLI tool `kubectl` installed, please follow [these instructions to install](https://kubernetes.io/docs/tasks/tools/).

### Configure `kubectl`

Configure `kubectl` to connect to your cluster by using `kubectl use-context my-cluster-name`.

* For GKE
  * Configure `gcloud` with `gcloud auth login`.
  * On the Google Cloud Console, the cluster page will have a `Connect` button, which will give a command to run locally that looks like

    `gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE_NAME --project PROJECT_NAME`.

  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl config use-context <gke context>` to access the cluster from `kubectl`.
* For EKS
  * [Configure your AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
  * Install [eksctl](https://eksctl.io/introduction/)
  * Run `eksctl utils write-kubeconfig --cluster=<CLUSTER NAME>` to make the context available to `kubectl`
  * Use `kubectl config get-contexts` to show the contexts available.
  * Run `kubectl config use-context <eks context>` to access the cluster with `kubectl`.

### Configure Logs

#### Default Configuration
Both `dev` and `stable` versions of Airbyte include a stand-alone `Minio` deployment. Airbyte publishes logs to this `Minio` deployment by default. This means Airbyte comes as a **self-contained Kubernetes deployment - no other configuration is required**.

So if you just want logs to be sent to the local `Minio` deployment, you do not need to change the values of any environment variables from what is currently on master.

#### Custom Configuration

Alternatively, if you want logs to be sent to a custom location, Airbyte currently supports logging to `Minio`, `S3` or `GCS`. The following instructions are for users wishing to log to their own `Minio` layer, `S3` bucket or `GCS` bucket.

The provided credentials require both read and write permissions. The logger attempts to create the log bucket if it does not exist.

##### Configuring Custom Minio Log Location

To write to a custom minio log location, replace the following variables in the `.env` file in the `kube/overlays/stable` directory:

```text
S3_LOG_BUCKET=<your_minio_bucket_to_write_logs_in>
AWS_ACCESS_KEY_ID=<your_minio_access_key>
AWS_SECRET_ACCESS_KEY=<your_minio_secret_key>
S3_MINIO_ENDPOINT=<endpoint_where_minio_is_deployed_at>
```

The `S3_PATH_STYLE_ACCESS` variable should remain `true`. The `S3_LOG_BUCKET_REGION` variable should remain empty.

##### Configuring Custom S3 Log Location

To write to a custom S3 log location, replace the following variables in the `.env` file in the `kube/overlays/stable` directory:

```text
S3_LOG_BUCKET=<your_s3_bucket_to_write_logs_in>
S3_LOG_BUCKET_REGION=<your_s3_bucket_region>
# Set this to empty.
S3_MINIO_ENDPOINT=
# Set this to empty.
S3_PATH_STYLE_ACCESS=
```
Additionally, replace the following variables in the `.secrets` file in the `kube/overlays/stable` directory:
```text
AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>
```

See [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) for instructions on creating an S3 bucket and [here](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) for instructions on creating AWS credentials.

##### Configuring Custom GCS Log Location

Create the GCP service account with read/write permission to the GCS log bucket.

1\) Base64 encode the GCP json secret.

```text
# The output of this command will be a Base64 string.
$ cat gcp.json | base64
```

2\) Populate the gcs-log-creds secrets with the Base64-encoded credential. This is as simple as taking the encoded credential from the previous step and adding it to the `secret-gcs-log-creds.yaml` file.

```text
apiVersion: v1
kind: Secret
metadata:
  name: gcs-log-creds
  namespace: default
data:
  gcp.json: <base64-encoded-string>
```

3\) Replace the following variables in the `.env` file in the `kube/overlays/stable` directory:

```text
GCS_LOG_BUCKET=<your_GCS_bucket_to_write_logs_in>
```

4\) Modify the `.secrets` file in the `kube/overlays/stable` directory
```text
# The path the GCS creds are written to. Unless you know what you are doing, use the below default value.
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcs-log-creds/gcp.json
```

See [here](https://cloud.google.com/storage/docs/creating-buckets) for instruction on creating a GCS bucket and [here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#iam-service-account-keys-create-console) for instruction on creating GCP credentials.

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

### Setting resource limits

* Core container pods
  * Instead of launching Airbyte with `kubectl apply -k kube/overlays/stable`, you can run with `kubectl apply -k kube/overlays/stable-with-resource-limits`.
  * The `kube/overlays/stable-with-resource-limits/set-resource-limits.yaml` file can be modified to provide different resource requirements for core pods.
* Connector pods
  * By default, connector pods launch without resource limits.
  * To add resource limits, configure the "Docker Resource Limits" section of the `.env` file in the overlay folder you're using.
* Volume sizes
  * You can modify `kube/resources/volume-*` files to specify different volume sizes for the persistent volumes backing Airbyte.

### Increasing job parallelism

The number of simultaneous jobs \(getting specs, checking connections, discovering schemas, and performing syncs\) is limited by a few factors. First of all, jobs are picked up and executed by airbyte-worker pods, so increasing the number of workers will allow more jobs to be processed in parallel.

The number of worker pods can be changed by increasing the number of replicas for the `airbyte-worker` deployment. An example of a Kustomization patch that increases this number can be seen in `airbyte/kube/overlays/dev-integration-test/kustomization.yaml` and `airbyte/kube/overlays/dev-integration-test/parallelize-worker.yaml`. The number of simultaneous jobs on a specific worker pod is also limited by the number of ports exposed by the worker deployment and set by `TEMPORAL_WORKER_PORTS` in your `.env` file. Without additional ports used to communicate to connector pods, jobs will start to run but will hang until ports become available.

You can also tune environment variables for the max simultaneous job types that can run on the worker pod by setting `MAX_SPEC_WORKERS`, `MAX_CHECK_WORKERS`, `MAX_DISCOVER_WORKERS`, `MAX_SYNC_WORKERS` for the worker pod deployment \(not in the `.env` file\). These values can be used if you want to create separate worker deployments for separate types of workers with different resource allocations.

### Cloud logging

Airbyte writes logs to two directories. App logs, including server and scheduler logs, are written to the `app-logging` directory. Job logs are written to the `job-logging` directory. Both directories live at the top-level e.g., the `app-logging` directory lives at `s3://log-bucket/app-logging` etc. These paths can change, so we recommend having a dedicated log bucket, and to not use this bucket for other purposes.

Airbyte publishes logs every minute. This means it is normal to see minute-long log delays. Each publish creates it's own log file, since Cloud Storages do not support append operations. This also mean it is normal to see hundreds of files in your log bucket.

Each log file is named `{yyyyMMddHH24mmss}_{podname}_{UUID}` and is not compressed. Users can view logs simply by navigating to the relevant folder and downloading the file for the time period in question.

See the [Known Issues](on-kubernetes.md#known-issues) section for planned logging improvements.

### Using an external DB

After [Issue \#3605](https://github.com/airbytehq/airbyte/issues/3605) is completed, users will be able to configure custom dbs instead of a simple `postgres` container running directly in Kubernetes. This separate instance \(preferable on a system like AWS RDS or Google Cloud SQL\) should be easier and safer to maintain than Postgres on your cluster.

## Known Issues

As we improve our Kubernetes offering, we would like to point out some common pain points. We are working on improving these. Please let us know if there are any other issues blocking your adoption of Airbyte or if you would like to contribute fixes to address any of these issues.

* Some UI operations have higher latency on Kubernetes than Docker-Compose. \([\#4233](https://github.com/airbytehq/airbyte/issues/4233)\)
* Logging to Azure Storage is not supported. \([\#4200](https://github.com/airbytehq/airbyte/issues/4200)\)
* Large log files might take a while to load. \([\#4201](https://github.com/airbytehq/airbyte/issues/4201)\)
* UI does not include configured buckets in the displayed log path. \([\#4204](https://github.com/airbytehq/airbyte/issues/4204)\)
* Logs are not reset when Airbyte is re-deployed. \([\#4235](https://github.com/airbytehq/airbyte/issues/4235)\)
* File sources reading from and file destinations writing to local mounts are not supported on Kubernetes.
* Cannot run custom DBT transformation. \([\#5091](https://github.com/airbytehq/airbyte/issues/5091)\)

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

Check out the [Helm Chart Readme](https://github.com/airbytehq/airbyte/tree/master/charts/airbyte)

## Operator Guide

### View API Server Logs

`kubectl logs deployments/airbyte-server` to view real-time logs. Logs can also be downloaded as a text file via the Admin tab in the UI.

### Connector Container Logs

Although all logs can be accessed by viewing the scheduler logs, connector container logs may be easier to understand when isolated by accessing from the Airbyte UI or the [Airbyte API](../api-documentation.md) for a specific job attempt. Connector pods launched by Airbyte will not relay logs directly to Kubernetes logging. You must access these logs through Airbyte.

### Upgrading Airbyte Kube

See [Upgrading K8s](../operator-guides/upgrading-airbyte.md).

### Resizing Volumes

To resize a volume, change the `.spec.resources.requests.storage` value. After re-applying, the mount should be extended if that operation is supported for your type of mount. For a production deployment, it's useful to track the usage of volumes to ensure they don't run out of space.

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

### Persistent storage on GKE regional cluster

Running Airbyte on GKE regional cluster requires enabling persistent regional storage. To do so, enable [CSI driver](https://cloud.google.com/kubernetes-engine/docs/how-to/persistent-volumes/gce-pd-csi-driver) on GKE. After enabling, add `storageClassName: standard-rwo` to the [volume-configs](https://github.com/airbytehq/airbyte/tree/86ee2ad05bccb4aca91df2fb07c412efde5ba71c/kube/resources/volume-configs.yaml) yaml.

`volume-configs.yaml` example:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: airbyte-volume-configs
  labels:
    airbyte: volume-configs
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
  storageClassName: standard-rwo
```

## Troubleshooting

If you run into any problems operating Airbyte on Kubernetes, please reach out on the `#issues` channel on our [Slack](https://slack.airbyte.io/) or [create an issue on GitHub](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=).

## Developing Airbyte on Kubernetes

[Read about the Kubernetes dev cycle!](https://docs.airbyte.io/contributing-to-airbyte/developing-on-kubernetes)

