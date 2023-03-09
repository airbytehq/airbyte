# Deploy Airbyte on Kubernetes

This page guides you through deploying Airbyte Open Source on Kubernetes. 

## Requirements

To test locally, you can use one of the following:

* [Docker Desktop](https://docs.docker.com/desktop/) with [Kubernetes](https://docs.docker.com/desktop/kubernetes/#enable-kubernetes) enabled
* [Minikube](https://docs.docker.com/desktop/kubernetes/#enable-kubernetes) with at least 4GB RAM
* [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)


To test on Google Kubernetes Engine(GKE), create a standard zonal cluster.

To test on  Amazon Elastic Kubernetes Service (Amazon EKS), install eksctl and create a cluster.

:::info 
Airbyte deployment is tested on GKE and EKS with version v1.19 and above. If you run into problems, reach out on the `#airbyte-help` channel in our Slack or create an issue on GitHub.
:::

## Install and configure `kubectl `

Install `kubectl` and run the following command to configure it and connect to your cluster:

```bash
kubectl use-context <my-cluster-name>
```

To configure `kubectl` in `GKE`:

1. Initialize the `gcloud` cli.
2. To view cluster details, go to the `cluster` page in the Google Cloud Console and click `connect`. Run the following command to test cluster details: 
`gcloud container clusters get-credentials <CLUSTER_NAME> --zone <ZONE_NAME> --project <PROJECT_NAME>`.
3. To view contexts, run: `kubectl config get-contexts`.
4. To access the cluster from `kubectl` run : `kubectl config use-context <gke context>`.

To configure `kubectl` in  `EKS`:

1. [Configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
2. Install [`eksctl`](https://eksctl.io/introduction/).
3. To Make contexts available to `kubectl`, run `eksctl utils write-kubeconfig --cluster=<CLUSTER NAME>`  
4. To view available contexts,  run `kubectl config get-contexts`.
5. To access the cluster, run `kubectl config use-context <eks context>`.

## Configure Logs

### Default configuration

Airbyte comes with a self-contained Kubernetes deployment and uses a stand-alone `Minio` deployment in both the `dev` and `stable` versions. Logs are published to the `Minio` deployment by default.

To send the logs to the local `Minio` deployment, make sure the specified credentials have both read and write permissions.

### Custom configuration

Airbyte supports logging to the `Minio` layer, `S3` bucket, and `GCS` bucket.

### Customize the `Minio` log location

To write to a custom location, update the following `.env` variable in the `kube/overlays/stable` directory (you will find this directory at the location you launched Airbyte)

``` bash
S3_LOG_BUCKET=<your_minio_bucket_to_write_logs_in>
AWS_ACCESS_KEY_ID=<your_minio_access_key>
AWS_SECRET_ACCESS_KEY=<your_minio_secret_key>
S3_MINIO_ENDPOINT=<endpoint_where_minio_is_deployed_at>
S3_LOG_BUCKET_REGION=
```
Set the` S3_PATH_STYLE_ACCESS variable to `true`.
Let the `S3_LOG_BUCKET_REGION` variable remain empty.

### Configure the Custom `S3` Log Location​

For the `S3` log location, create an S3 bucket with your AWS credentials.

To write to a custom location, update the following `.env` variable in the `kube/overlays/stable` directory (you can find this directory at the location you launched Airbyte)

``` bash
S3_LOG_BUCKET=<your_s3_bucket_to_write_logs_in>
S3_LOG_BUCKET_REGION=<your_s3_bucket_region>
# Set this to empty.
S3_MINIO_ENDPOINT=
# Set this to empty.
S3_PATH_STYLE_ACCESS=
```
Replace the following variable in `.secrets` file in the `kube/overlays/stable` directory:

```bash
AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>
```

### Configure the Custom GCS Log Location​

Create a GCS bucket and  GCP credentials if you haven’t already. Make sure your GCS log bucket has read/write permission.

To configure the custom log location:

Base encode the GCP JSON secret with the following command:

```bash
# The output of this command will be a Base64 string.
$ cat gcp.json | base64
```
To populate the `gcs-log-creds` secrets with the Base64-encoded credential, take the encoded GCP JSON secret from the previous step and add it to `secret-gcs-log-creds.yaml` file as the value for `gcp.json` key. 

```bash
apiVersion: v1
kind: Secret
metadata:
 name: gcs-log-creds
 namespace: default
data:
 gcp.json: <base64-encoded-string>
```

In the `kube/overlays/stable` directory, update the  `GCS_LOG_BUCKET` with your GCS log bucket credentials:

```bash
GCS_LOG_BUCKET=<your_GCS_bucket_to_write_logs_in>
```

Modify `GOOGLE_APPLICATION_CREDENTIALS` to the path to `gcp.json` in the `.secrets` file at `kube/overlays/stable` directory.

```bash
# The path the GCS creds are written to. Unless you know what you are doing, use the below default value.

GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcs-log-creds/gcp.json
```


## Launch Airbyte

The following commands will help you launch Airbyte:

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
kubectl apply -k kube/overlays/stable
```

To check the pod status, run `kubectl get pods | grep airbyte`.

If you are on Windows, run `kubectl get pods` to the list of pods.

Run `kubectl port-forward svc/airbyte-webapp-svc 8000:80`  to allow access to the UI/API.
Navigate to http://localhost:8000 in your browser to verify the deployment.

## Deploy Airbyte on Kubernetes in production

### Set resource limits

* Core container pods 

  * To provide different resource requirements for core pods, set resource limits in the  `kube/overlays/stable-with-resource-limits/set-resource-limits.yaml` file.

  * To launch Airbyte with new resource limits, 	use the `kubectl apply -k kube/overlays/stable-with-resource-limits command.

* Connector pods
	
  * By default, connector pods launch without resource limits. To add resource limit, configure the `Docker resource limits` section of the `.env` file in the `kube/overlays` directory.

* Volume sizes

  * To specify different volume sizes for the persistent volume backing Airbyte, modify `kube/resources/volume-*`  files.


### Increase job parallelism

The ability to run parallel jobs like getting specs, checking connections, discovering schemas and performing syncs is limited by a few factors. `Airbyte-worker-pods` picks and executes the job. Increasing the number of workers will allow more jobs to be processed.

To create more worker pods, increase the number of replicas for the `airbyte-worker` deployment. Refer to examples of increasing worker pods in a Kustomization patch in `airbyte/kube/overlays/dev-integration-test/kustomization.yaml` and `airbyte/kube/overlays/dev-integration-test/parallelize-worker.yaml` 
 
To limit the exposed ports in `.env`  file, set the value to `TEMPORAL_WORKER_PORTS`. You can run jobs parallely at each exposed port.
If you do not have enough ports to communicate, the jobs might not complete or halt until ports become available.

You can set a limit for the maximum parallel jobs that run on the pod. Set the value to `MAX_SPEC_WORKERS`, `MAX_CHECK_WORKERS`, `MAX_DISCOVER_WORKERS`, and `MAX_SYNC_WORKERS` variables in the worker pod deployment and not in `.env` file. You can use these values to create separate worker deployments for each type of worker with different resource allocations.


### Cloud Logging

Airbyte writes logs to two different directories: The `App-logging` directory and the `job-logging` directory. App logs, server logs, and scheduler logs are written to the `app-logging` directory. Job logs are written to the `job-logging` directory. Both directories live at the top level. For example, the app logging directory may live at `s3://log-bucket/app-logging`. We recommend having a dedicated logging bucket and not using it for other purposes.

Airbyte publishes logs every minute, so it’s normal to have minute-long log delays. Cloud Storages do not support append operations. Each publisher creates its own log files, which means you will have hundreds of files in your log bucket.

Each log file is uncompressed and named `{yyyyMMddHH24mmss}_{podname}_{UUID}`.
To view logs, navigate to the relevant folder and download the file for the time period you want.

### Use external databases

You can configure a custom database instead of a simple `postgres` container in Kubernetes. This separate instance (AWS RDS or Google Cloud SQL) should be easier and safer to maintain than Postgres on your cluster.

## Customize Airbytes Manifests

We use Kustomize to allow configuration for different environments. Our shared resources are in the `kube/resources` directory. We recommend defining overlays for each environment and creating your own overlay to customize your deployments. The overlay can live in your own version control system.
An example of `kustomization.yaml`  file:

```bash
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases: https://github.com/airbytehq/airbyte.git/kube/overlays/stable?ref=master
```

### View Raw Manifests

To view manifests for a specific overlay that Kustomize applies to your Kubernetes cluster, run `kubectl kustomize kube/overlays/stable`. 


### Helm Charts

For detailed information about Helm Charts, refer to the charts [readme](https://github.com/airbytehq/airbyte/tree/master/charts/airbyte) file.


## Operator Guide

### View API server logs

You can view real-time logs in `kubectl logs deployments/airbyte-server` directory and download them from the Admin Tab.

### Connector Container Logs​

All logs can be accessed by viewing the scheduler logs. As for connector container logs, use Airbyte UI or Airbyte API to isolate them for a specific job attempt and for easier understanding. Connector pods launched by Airbyte will not relay logs directly to Kubernetes logging. You must access these logs through Airbyte.


### Resize Volumes

To resize a volume, change the `.spec.resources.requests.storage` value. After re-applying, extend the mount(if that operation is supported for your mount type). For a production deployment, track the usage of volumes to ensure they don't run out of space.

### Copy Files in Volumes

To copy files, use the [`cp` command in kubectl](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#cp).

### List Files

To list files, run:

`kubectl exec -it airbyte-server-6b5747df5c-bj4fx ls /tmp/workspace/8`

### Read Files

To read files, run:

`kubectl exec -it airbyte-server-6b5747df5c-bj4fx cat /tmp/workspace/8/0/logs.log`

### Persistent storage on Google Kubernetes Engine(GKE) regional cluster

Running Airbyte on a GKE regional cluster requires enabling persistent regional storage. Start with [enabling CSE driver](https://cloud.google.com/kubernetes-engine/docs/how-to/persistent-volumes/gce-pd-csi-driver#enabling_the_on_an_existing_cluster) on GKE and add `storageClassName: standard-rwo` to the [volume-configs.yamll](https://github.com/airbytehq/airbyte/blob/86ee2ad05bccb4aca91df2fb07c412efde5ba71c/kube/resources/volume-configs.yaml).

Sample `volume-configs.yaml` file:

```bash
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
If you encounter any issues, reach out to our community on [Slack](https://slack.airbyte.com/).



