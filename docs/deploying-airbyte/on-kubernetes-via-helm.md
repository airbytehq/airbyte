# Deploy Airbyte on Kubernetes using Helm (Beta)

## Overview

Airbyte allows scaling sync workloads horizontally using Kubernetes. The core components \(api server, scheduler, etc\) run as deployments while the scheduler launches connector-related pods on different nodes.

## Quickstart

If you don't want to configure your own Kubernetes cluster and Airbyte instance, you can use the free, open-source project [Plural](https://www.plural.sh/) to bring up a Kubernetes cluster and Airbyte for you. Use [this guide](on-plural.md) to get started.

Alternatively, you can deploy Airbyte on [Restack](https://www.restack.io) to provision your Kubernetes cluster on AWS. Follow [this guide](on-restack.md) to get started.

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

For GKE:

1. Configure `gcloud` with `gcloud auth login`.
2. On the Google Cloud Console, the cluster page will have a `Connect` button, which will give a command to run locally that looks like

    `gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE_NAME --project $PROJECT_NAME`.

3. Use `kubectl config get-contexts` to show the contexts available.
4. Run `kubectl config use-context $GKE_CONTEXT` to access the cluster from `kubectl`.

For EKS:

1. [Configure your AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
2. Install [eksctl](https://eksctl.io/introduction/)
3. Run `eksctl utils write-kubeconfig --cluster=<CLUSTER NAME>` to make the context available to `kubectl`
4. Use `kubectl config get-contexts` to show the contexts available.
5. Run `kubectl config use-context <eks context>` to access the cluster with `kubectl`.

### Install helm

To install helm simply run:

For MacOS:
  
  `brew install helm`

For Linux:

1. Download installer script `curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3`
2. Assign required premissions `chmod 700 get_helm.sh`
3. Run script `./get_helm.sh`

### Add Helm Repository

From now charts are stored in helm-repo thus there're no need to clone the repo each time you need to deploy the chart.

To add remote helm repo simply run: `helm repo add airbyte https://airbytehq.github.io/helm-charts`.

Where `airbyte` is the name of the repository that will be indexed locally.

After adding the repo, perform the repo indexing process by running `helm repo update`.

After this you can browse all charts uploaded to repository by running `helm search repo airbyte`

It'll produce the output below:

```text
NAME                            CHART VERSION   APP VERSION     DESCRIPTION                             
airbyte-oss/airbyte             0.30.23         0.39.37-alpha   Helm chart to deploy airbyte            
airbyte-oss/airbyte-bootloader  0.30.23         0.39.37-alpha   Helm chart to deploy airbyte-bootloader 
airbyte-oss/pod-sweeper         0.30.23         0.39.37-alpha   Helm chart to deploy airbyte-pod-sweeper
airbyte-oss/server              0.30.23         0.39.37-alpha   Helm chart to deploy airbyte-server     
airbyte-oss/temporal            0.30.23         0.39.37-alpha   Helm chart to deploy airbyte-temporal   
airbyte-oss/webapp              0.30.23         0.39.37-alpha   Helm chart to deploy airbyte-webapp     
airbyte-oss/worker              0.30.23         0.39.37-alpha   Helm chart to deploy airbyte-worker  
```

## Deploy Airbyte

### Default deployment

If you don't intend to customise your deployment, you can deploy airbyte as is with default values.

In order to do so, run the command: 
```
helm install %release_name% airbyte/airbyte
```

### Custom deployment

In order to customize your deployment, you need to create `values.yaml` file in the local folder and populate it with default configuration override values.

`values.yaml` example can be located in [charts/airbyte](https://github.com/airbytehq/airbyte/blob/master/charts/airbyte/values.yaml) folder of the Airbyte repository.

After specifying your own configuration, run the following command:

```text
helm install --values path/to/values.yaml %release_name% airbyte/airbyte
```

## Migrate from old charts to new ones

Starting from `0.39.37-alpha` we've revisited helm charts structure and separated all components of airbyte into their own independent charts, thus by allowing our developers to test single component without deploying airbyte as a whole and by upgrading single component at a time.

In most cases upgrade from older monolith chart to a new one should go without any issue, but if you've configured custom logging or specified custom configuration of DB or Logging then follow the instructions listed bellow

### Minio migration

Since the latest release of bitnami/minio chart, they've changed the way of setting up the credentials for accessing the minio. (written mid-2022)

Going forward in new version you need to specify the following values in values yaml for user/password instead old one

Before:
```text
minio:
  rootUser: airbyte-user
  rootPassword: airbyte-password-123
```
After:
```text
minio:
  auth:
    rootUser: minio
    rootPassword: minio123

```

Before upgrading the chart update values.yaml as stated above and then run:

* Get the old rootPassword by running `export ROOT_PASSWORD=$(kubectl get secret --namespace "default" %release_name%-minio -o jsonpath="{.data.root-password}" | base64 -d)`
* Perform upgrade of chart by running `helm upgrade %release_name% airbyte/airbyte --set auth.rootPassword=$ROOT_PASSWORD`
  * If you get an error about setting the auth.rootPassword, then you forgot to update the `values.yaml` file

### Custom logging and jobs configuration

Starting from `0.39.37-alpha` if you've configured logging yourself using `logging or jobs` section of `values.yaml` file, you need to update your configuration so you can continue to use your custom logging and jobs configuration.

Simply declare global value in `values.yaml` file and move everything related to logging and jobs under that section like in the example bellow:

```text
global:
    logging:
        %your_logging_options_here%
    jobs:
        %your_jobs_options_here%
```

After updating `values.yaml` simply upgrade your chart by running command: 
```shell
helm upgrade -f path/to/values.yaml %release_name% airbyte/airbyte
```

### Database external secrets

If you're using external DB secrets, then provide them in `values.yaml` under global.database section in the following format:

```text
  database:
    secretName: "myOctaviaSecret"
    secretValue: "postgresql-password"
    host: "example.com"
    port: "5432"
```

And upgrade the chart by running: 
```shell
helm upgrade -f path/to/values.yaml %release_name% airbyte/airbyte
```
