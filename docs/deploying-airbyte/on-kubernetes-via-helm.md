# Deploy Airbyte on Kubernetes using Helm

## Overview

Airbyte allows scaling sync workloads horizontally using Kubernetes. The core components \(api
server, worker, etc\) run as deployments while the scheduler launches connector-related pods on
different nodes.

## Quickstart

If you don't want to configure your own Kubernetes cluster and Airbyte instance, you can use the
free, open-source project [Plural](https://www.plural.sh/) to bring up a Kubernetes cluster and
Airbyte for you. Use [this guide](on-plural.md) to get started.

Alternatively, you can deploy Airbyte on [Restack](https://www.restack.io) to provision your
Kubernetes cluster on AWS. Follow [this guide](on-restack.md) to get started.

:::note

Airbyte running on Self-Hosted Kubernetes doesn't support DBT Transformations. Please refer to
[#5901](https://github.com/airbytehq/airbyte/issues/5091)

:::

:::note

Airbyte Kubernetes Community Edition does not support basic auth by default. To enable basic auth,
consider adding a reverse proxy in front of Airbyte.

:::

## Getting Started

### Cluster Setup

For local testing we recommend following one of the following setup guides:

- [Docker Desktop \(Mac\)](https://docs.docker.com/desktop/kubernetes)
- [Minikube](https://minikube.sigs.k8s.io/docs/start)
  - NOTE: Start Minikube with at least 4gb RAM with `minikube start --memory=4000`
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)

For testing on GKE you can
[create a cluster with the command line or the Cloud Console UI](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster).

For testing on EKS you can [install eksctl](https://eksctl.io/introduction/) and run
`eksctl create cluster` to create an EKS cluster/VPC/subnets/etc. This process should take 10-15
minutes.

For production, Airbyte should function on most clusters v1.19 and above. We have tested support on
GKE and EKS. If you run into a problem starting Airbyte, please reach out on the `#troubleshooting`
channel on our [Slack](https://slack.airbyte.io/) or
[create an issue on GitHub](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=).

### Install `kubectl`

If you do not already have the CLI tool `kubectl` installed, please follow
[these instructions to install](https://kubernetes.io/docs/tasks/tools/).

### Configure `kubectl`

Configure `kubectl` to connect to your cluster by using `kubectl use-context my-cluster-name`.

For GKE:

1. Configure `gcloud` with `gcloud auth login`.
2. On the Google Cloud Console, the cluster page will have a `Connect` button, which will give a
   command to run locally that looks like

   `gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE_NAME --project $PROJECT_NAME`.

3. Use `kubectl config get-contexts` to show the contexts available.
4. Run `kubectl config use-context $GKE_CONTEXT` to access the cluster from `kubectl`.

For EKS:

1. [Configure your AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
   to connect to your project.
2. Install [eksctl](https://eksctl.io/introduction/)
3. Run `eksctl utils write-kubeconfig --cluster=<CLUSTER NAME>` to make the context available to
   `kubectl`
4. Use `kubectl config get-contexts` to show the contexts available.
5. Run `kubectl config use-context <eks context>` to access the cluster with `kubectl`.

### Install helm

To install helm simply run:

For MacOS:

`brew install helm`

For Linux:

1. Download installer script
   `curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3`
2. Assign required premissions `chmod 700 get_helm.sh`
3. Run script `./get_helm.sh`

### Add Helm Repository

From now charts are stored in helm-repo thus there're no need to clone the repo each time you need
to deploy the chart.

To add remote helm repo simply run: `helm repo add airbyte https://airbytehq.github.io/helm-charts`.

Where `airbyte` is the name of the repository that will be indexed locally.

After adding the repo, perform the repo indexing process by running `helm repo update`.

After this you can browse all charts uploaded to repository by running `helm search repo airbyte`

It'll produce output similar to below:

```text
NAME                            	CHART VERSION	APP VERSION	DESCRIPTION
airbyte/airbyte                 	0.49.9       	0.50.33    	Helm chart to deploy airbyte
airbyte/airbyte-api-server      	0.49.9       	0.50.33    	Helm chart to deploy airbyte-api-server
airbyte/airbyte-bootloader      	0.49.9       	0.50.33    	Helm chart to deploy airbyte-bootloader
airbyte/connector-builder-server	0.49.9       	0.50.33    	Helm chart to deploy airbyte-connector-builder-...
airbyte/cron                    	0.49.9       	0.50.33    	Helm chart to deploy airbyte-cron
airbyte/metrics                 	0.49.9       	0.50.33    	Helm chart to deploy airbyte-metrics
airbyte/pod-sweeper             	0.49.9       	0.50.33    	Helm chart to deploy airbyte-pod-sweeper
airbyte/server                  	0.49.9       	0.50.33    	Helm chart to deploy airbyte-server
airbyte/temporal                	0.49.9       	0.50.33    	Helm chart to deploy airbyte-temporal
airbyte/webapp                  	0.49.9       	0.50.33    	Helm chart to deploy airbyte-webapp
airbyte/worker                  	0.49.9       	0.50.33    	Helm chart to deploy airbyte-worker
```

## Deploy Airbyte

### Default deployment

If you don't intend to customise your deployment, you can deploy airbyte as is with default values.

In order to do so, run the command:

```
helm install %release_name% airbyte/airbyte
```

**Note**: `release_name` should only contain lowercase letters and optionally dashes (`release_name`
must start with a letter).

### Custom deployment

In order to customize your deployment, you need to create `values.yaml` file in the local folder and
populate it with default configuration override values.

`values.yaml` example can be located in
[charts/airbyte](https://github.com/airbytehq/airbyte-platform/blob/main/charts/airbyte/values.yaml)
folder of the Airbyte repository.

After specifying your own configuration, run the following command:

```text
helm install --values path/to/values.yaml %release_name% airbyte/airbyte
```

### External Logs with S3

:::info

S3 logging was tested on
[Airbyte Helm Chart Version 0.50.13](https://artifacthub.io/packages/helm/airbyte/airbyte/0.50.13)

:::

Create a file called `airbyte-logs-secrets.yaml` to store the AWS Keys and other informations:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-logs-secrets
type: Opaque
stringData:
  AWS_KEY: <AWS_KEY>
  AWS_SECRET_KEY: <AWS_SECRET_KEY>
  S3_LOG_BUCKET: <BUCKET_NAME>
  S3_LOG_BUCKET_REGION: <REGION>
```

Run `kubectl apply -f airbyte-logs-secrets.yaml -n <NAMESPACE>` to create the secret in the
namespace you're using Airbyte. This file contains more than just the keys but it needs for now.
Future updates will make the configuration easier.

Change the global section to use `S3` external logs.

```yaml
global:
  # <...>
  state:
    # -- Determines which state storage will be utilized; "MINIO", "S3", or "GCS"
    storage:
      type: "S3"
  # <...>
  logs:
    accessKey:
      password: ""
      existingSecret: "airbyte-logs-secrets"
      existingSecretKey: "AWS_KEY"
    secretKey:
      password: ""
      existingSecret: "airbyte-logs-secrets"
      existingSecretKey: "AWS_SECRET_KEY"
  # <...>
  storage:
    type: "S3"

  minio:
    # Change from true to false
    enabled: false
    nodeSelector: {}
    tolerations: []
    affinity: {}
```

GCS Logging information is below but you can try to use `External Minio` as well but it was not
tested yet. Feel free to run tests and update the documentation.

Add extra env variables to the following blocks:

```yaml
worker:
  extraEnv:
    - name: AWS_ACCESS_KEY_ID
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_KEY
    - name: AWS_SECRET_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_SECRET_KEY
    - name: STATE_STORAGE_S3_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_KEY
    - name: STATE_STORAGE_S3_SECRET_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_SECRET_KEY
    - name: STATE_STORAGE_S3_BUCKET_NAME
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: S3_LOG_BUCKET
    - name: STATE_STORAGE_S3_REGION
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: S3_LOG_BUCKET_REGION
```

and also edit the server block:

```yaml
server:
  extraEnv:
    - name: AWS_ACCESS_KEY_ID
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_KEY
    - name: AWS_SECRET_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_SECRET_KEY
    - name: STATE_STORAGE_S3_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_KEY
    - name: STATE_STORAGE_S3_SECRET_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: AWS_SECRET_KEY
    - name: STATE_STORAGE_S3_BUCKET_NAME
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: S3_LOG_BUCKET
    - name: STATE_STORAGE_S3_REGION
      valueFrom:
        secretKeyRef:
          name: airbyte-logs-secrets
          key: S3_LOG_BUCKET_REGION
```

Than run:
`helm upgrade --install %RELEASE_NAME% airbyte/airbyte -n <NAMESPACE> --values /path/to/values.yaml --version 0.50.13`

### External Logs with GCS

:::info

GCS Logging is similar to the approach taken for S3 above, with a few small differences
GCS logging was tested on [Airbyte Helm Chart Version 0.54.69](https://artifacthub.io/packages/helm/airbyte/airbyte/0.54.69)

:::

#### Create Google Cloud Storage Bucket

1. **Access Google Cloud Console**: Go to the Google Cloud Console and select or create a project
   where you want to create the bucket.
2. **Open Cloud Storage**: Navigate to "Storage" > "Browser" in the left-side menu.
3. **Create Bucket**: Click on "Create bucket". Give your bucket a unique name, select a region for the bucket, and configure other settings such as storage class and access control according to your requirements. Finally, click "Create". The buckect will be referenced as `<bucket_name>`

#### Create Google Cloud Service Account

1. **Open IAM & Admin**: In the Cloud Console, navigate to "IAM & Admin" > "Service Accounts".
2. **Create Service Account**: Click "Create Service Account", enter a name, description, and then click "Create".
3. **Grant Permissions**: Assign the role of "Storage Object Admin" to the service account by selecting it from the role list.
4. **Create Key**: After creating the service account, click on it, go to the "Keys" tab, and then click "Add Key" > "Create new key". Choose JSON as the key type and click "Create". The key file will be downloaded automatically to your computer.
5. **Encode Key**: Encode GCP credentials file contents using Base64. This key will be referenced as `<encoded_key>`

#### Update the values.yaml with the GCS Logging Information below

Update the following Environment Variables in the global section:

```
global:
 state:
   storage:
     type: "GCS"

 logs:
   storage:
     type: "GCS"
   gcs:
     bucket: "<bucket_name>"
     credentials: "/secrets/gcs-log-creds/gcp.json"
     credentialsJson: "<encoded_key>"
```

Update the following Environment Variables in the worker section:

```
worker:

 extraEnv:
   - name: STATE_STORAGE_GCS_BUCKET_NAME
     value: <bucket_name>
   - name: STATE_STORAGE_GCS_APPLICATION_CREDENTIALS
     value: /secrets/gcs-log-creds/gcp.json
   - name: CONTAINER_ORCHESTRATOR_SECRET_NAME
     value: <%RELEASE_NAME%>-gcs-log-creds
   - name: CONTAINER_ORCHESTRATOR_SECRET_MOUNT_PATH
     value: /secrets/gcs-log-creds
```

Then run:
`helm upgrade --install %RELEASE_NAME% airbyte/airbyte -n <NAMESPACE> --values /path/to/values.yaml --version 0.54.69`

### External Airbyte Database

:::info

This was tested using
[Airbyte Helm Chart Version 0.50.13](https://artifacthub.io/packages/helm/airbyte/airbyte/0.50.13).
Previous or newer version can change how the external database can be configured.

:::

The Airbyte Database only works with Postgres 13. Make sure the database is accessible inside the
cluster using `busy-box` service using `telnet` or `ping` command.

:::warning

If you're using the external database for the first time you must ensure the database you're going
to use exists. The default database Airbyte will try to use is `airbyte` but you can modified it in
the `values.yaml`.

:::

:::warning

You can use only one database to a one Airbyte Helm deployment. If you try to use the same database
for a different deployment it will have conflict with Temporal internal databases.

:::

Create a Kubernetes secret to store the database password. Save the file as `db-secrets.yaml`.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
type: Opaque
stringData:
  DATABASE_PASSWORD: <PASSWORD>
```

Run `kubectl apply -f db-secrets.yaml -n <NAMESPACE>` to create the secret in the namespace you're
using Airbyte.

Afterward, modify the following blocks in the Helm Chart `values.yaml` file:

```yaml
postgresql:
  # Change the value from true to false.
  enabled: false
```

Then:

```yaml
externalDatabase:
  # Add the host, username and database name you're using.
  host: <HOST>
  user: <USERNAME>
  database: <DATABASE_NAME>
  password: ""
  existingSecret: "db-secrets"
  existingSecretPasswordKey: "DATABASE_PASSWORD"
  port: 5432
  jdbcUrl: ""
```

Keep password empty as the Chart will use the `db-secrets` value. Edit only the host, username, and
database name. If your database is using a differnet `port` or need an special `jdbcUrl` you can
edit here. This wasn't fully tested yet.

Next, reference the secret in the global section:

```yaml
global:
  database:
    secretName: "db-secrets"
    secretValue: "DATABASE_PASSWORD"
```

Unfortunately, the `airbyte-bootloader` configuration uses this variable. Future improvements are
planned.

Upgrade the chart by running:

```shell
helm upgrade --install %RELEASE_NAME% airbyte/airbyte -n <NAMESPACE> --values /path/to/values.yaml --version 0.50.13
```

## Migrate from old chart to Airbyte v0.52.0 and latest chart version

To assist with upgrading to Airbyte App version 0.52.0 and higher with the latest Helm Charts, we've
simplified and consolidated several configuration options. Here's a breakdown of the changes:

**Application.yaml Updates**:

- We've streamlined the configuration for logs and state storage.
- Instead of separate configurations for logs and state, we now have a unified storage
  configuration.
- The proposed changes involve specifying the storage type and bucket names directly, along with
  credentials where necessary.

**Helm Configuration Updates:**

- The global configuration now includes a simplified storage section specifying the type and bucket
  names for logs, state, and workload output.
- Credentials for MinIO are now set directly in the Helm values, ensuring smoother integration.
- Unused configurations have been removed, and configurations have been aligned with the simplified
  application.yaml.

**Technical Details and Renaming:**

- We've renamed or consolidated several environment variables for clarity and consistency.
- Unused methods and classes have been removed, ensuring a cleaner codebase.
- Some configurations have been split into separate files for better management and compatibility
  with different storage options.

**Additional Changes:**

- We've added support for workload output storage explicitly, improving flexibility and clarity in
  configuration.
- The Helm charts have been updated to reflect these changes, removing or replacing old environment
  variables for storage configuration.
- These changes aim to simplify configuration management and improve the overall user experience
  during upgrades. Please review these updates and let us know if you have any questions or need
  further assistance.

### **Migration Steps**

This guide aims to assist customers upgrading to the latest version of the Airbyte Helm charts,
specifically those using custom configurations for external logging and databases with AWS (S3) and
GCS (Google Cloud Buckets).

### **For AWS S3 Users**

#### **Prerequisites**

- Access to your Kubernetes cluster where Airbyte is deployed.
- Helm and kubectl installed and configured on your machine.
- Existing Airbyte deployment using AWS S3 for storage and AWS Secrets Manager for secret
  management.

#### **Migration Steps**

1. **Creating or Updating Kubernetes Secrets**

If using AWS access keys, create a Kubernetes secret to store these credentials. If relying on an
IAM role from an instance profile, this step can be skipped. Apply the following Kubernetes
manifest, replacing the example AWS credentials with your actual credentials:

```yaml
# Replace the example AWS credentials below with your actual credentials.
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  s3-access-key-id: AKIAIOSFODNN7EXAMPLE # Enter your AWS Access Key ID here
  s3-secret-access-key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY # Enter your AWS Secret Access Key here
```

2. **Update Airbyte Configuration**

   In your `airbyte.yml` configuration file, add the following configuration, adjusting
   `<aws-region>` to match your AWS region:

   ```yaml
   global:
     storage:
       type: s3
       storageSecretName: airbyte-config-secrets
       bucket:
         log: airbyte-storage
         state: airbyte-storage
         workloadOutput: airbyte-storage
       s3:
         region: <aws-region>
         authenticationType: credentials # Use "credentials" or "instanceProfile"
         accessKeyIdSecretKey: aws-secret-manager-access-key-id # Omit if using instanceProfile
         secretAccessKeySecretKey: aws-secret-manager-secret-access-key # Omit if using instanceProfile

     secretsManager:
       type: awsSecretManager
       storageSecretName: airbyte-config-secrets
       awsSecretManager:
         region: <aws-region>
         authenticationType: credentials # Use "credentials" or "instanceProfile"
         accessKeyIdSecretKey: aws-secret-manager-access-key-id # Omit if using instanceProfile
         secretAccessKeySecretKey: aws-secret-manager-secret-access-key # Omit if using instanceProfile
         tags:
           - key: team
             value: deployment
           - key: business-unit
             value: engineering
   ```

3. **Remove Deprecated Configuration from `values.yaml`**

   Edit your `values.yaml` or `airbyte-pro-values.yaml` files to remove any deprecated storage and
   secrets manager environment variables related to S3 and AWS Secrets Manager. Ensure
   configurations like `state.storage.type: "S3"` and AWS access keys under `server.extraEnv` and
   `worker.extraEnv` are removed.

### **For GCS Users**

#### **Prerequisites**

- Access to your Kubernetes cluster where Airbyte is deployed.
- Helm and kubectl installed and configured on your machine.
- Existing Airbyte deployment using Google Cloud Storage (GCS) and Google Secret Manager (GSM) for
  secret management.

#### **Migration Steps**

1. **Setting Up or Updating Kubernetes Secrets**

   For Google Secret Manager, you may use existing credentials or create new ones. Apply a
   Kubernetes manifest like below, replacing `<CREDENTIALS_JSON_BLOB>` with your GCP credentials
   JSON blob:

   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: gcp-cred-secrets
   type: Opaque
   stringData:
     gcp.json: <CREDENTIALS_JSON_BLOB>
   ```

   Or use `kubectl` to create the secret directly from a file:

   ```sh
   kubectl create secret generic gcp-cred-secrets --from-file=gcp.json=<path-to-your-credentials-file>.json
   ```

2. **Update Airbyte Configuration**

   In your `airbyte.yml` configuration file, add the following configuration, adjusting
   `<project-id>` to match your GCP project ID:

   ```yaml
   global:
     storage:
       type: gcs
       storageSecretName: gcp-cred-secrets
       bucket:
         log: airbyte-storage
         state: airbyte-storage
         workloadOutput: airbyte-storage
       gcs:
         authenticationType: credentials
         projectId: <project-id>
         credentialsPath: /secrets/gcs-log-creds/gcp.json

     secretsManager:
       type: googleSecretManager
       storageSecretName: gcp-cred-secrets
       googleSecretManager:
         authenticationType: credentials
         projectId: <project-id>
         credentialsSecretKey: gcp-creds.json
   ```

3. **Remove Deprecated Configuration from `values.yaml`**

   Edit your `values.yaml` files to remove any deprecated storage and secrets manager environment
   variables related to GCS. Ensure configurations like `global.state.storage.type: "GCS"` and GCS
   credentials paths under `extraEnv` are removed.

This guide ensures that you leverage the latest Helm chart configurations for Airbyte, aligning with
best practices for managing storage and secrets in Kubernetes environments for AWS and GCS users.
