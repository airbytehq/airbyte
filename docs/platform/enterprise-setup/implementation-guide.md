---
products: oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import ContainerProviders from '@site/static/_docker_image_registries.md';

# Implementation Guide

Once you [have a license key](https://airbyte.com/company/talk-to-sales), you can deploy [Self-Managed Enterprise](./README.md) using the following instructions.

Airbyte Self-Managed Enterprise must be deployed using Kubernetes. This is to enable Airbyte's best performance and scale. The core Airbyte components (`server`, `workload-launcher`) run as deployments. The `workload-launcher` is responsible for managing connector-related pods (`check`, `discover`, `read`, `write`, `orchestrator`).

:::note
Airbyte has begun rolling out a new Helm chart called Helm chart V2. The instructions on this page describe both V1 and V2 requirements. Airbyte recommends using Helm chart V2 from the start. The new chart will become mandatory in the future and you can avoid having to upgrade later.
:::

## Prerequisites

### Infrastructure Prerequisites

For a production-ready deployment of Self-Managed Enterprise, the following infrastructure components are required. Deploy to Amazon EKS or Google Kubernetes Engine. The following diagram illustrates a typical Airbyte deployment running on AWS:

![AWS Architecture Diagram](./assets/self-managed-enterprise-aws.png)

Prior to deploying Self-Managed Enterprise, Airbyte recommends having each of the following infrastructure components ready to go. When possible, it's easiest to have all components running in the same [VPC](https://docs.aws.amazon.com/eks/latest/userguide/network_reqs.html). The provided recommendations are for customers deploying to AWS:

| Component                | Recommendation                                                                                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kubernetes Cluster       | Amazon EKS cluster running on EC2 instances in [2 or more availability zones](https://docs.aws.amazon.com/eks/latest/userguide/disaster-recovery-resiliency.html) on a minimum of 6 nodes. |
| Ingress                  | [Amazon ALB](#configuring-ingress) and a URL for users to access the Airbyte UI or make API requests.                                                                     |
| Object Storage           | [Amazon S3 bucket](#configuring-external-logging) with two directories for log and state storage.                                                                         |
| Dedicated Database       | [Amazon RDS Postgres](#configuring-the-airbyte-database) with at least one read replica.                                                                                  |
| External Secrets Manager | [Amazon Secrets Manager](/platform/operator-guides/configuring-airbyte#secrets) for storing connector secrets.                                                                     |

A few notes on Kubernetes cluster provisioning for Airbyte Self-Managed Enterprise:

- Airbyte supports Amazon Elastic Kubernetes Service (EKS) on EC2, Google Kubernetes Engine (GKE) on Google Compute Engine (GCE), and Azure Kubernetes Service (AKS).
- Airbyte recommends running Airbyte on memory-optimized instances, such as M7i / M7g instance types.
- While Airbyte supports GKE Autopilot, it doesn't support Amazon EKS on Fargate.
- You should run Airbyte on instances with at least 2 cores and 8 gigabytes of RAM.

We require you to install and configure the following Kubernetes tooling:

1. Install `helm` by following [these instructions](https://helm.sh/docs/intro/install/)
2. Install `kubectl` by following [these instructions](https://kubernetes.io/docs/tasks/tools/).
3. Configure `kubectl` to connect to your cluster by using `kubectl use-context my-cluster-name`:

<details>
<summary>Configure kubectl to connect to your cluster</summary>

<Tabs>
<TabItem value="Amazon EKS" label="Amazon EKS" default>

1. Configure your [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
2. Install [eksctl](https://eksctl.io/introduction/).
3. Run `eksctl utils write-kubeconfig --cluster=$CLUSTER_NAME` to make the context available to kubectl.
4. Use `kubectl config get-contexts` to show the available contexts.
5. Run `kubectl config use-context $EKS_CONTEXT` to access the cluster with kubectl.

</TabItem>

<TabItem value="GKE" label="GKE">

1. Configure `gcloud` with `gcloud auth login`.
2. On the Google Cloud Console, the cluster page will have a "Connect" button, with a command to run locally: `gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE_NAME --project $PROJECT_NAME`.
3. Use `kubectl config get-contexts` to show the available contexts.
4. Run `kubectl config use-context $EKS_CONTEXT` to access the cluster with kubectl.

</TabItem>
</Tabs>

</details>

We also require you to create a Kubernetes namespace for your Airbyte deployment:

```
kubectl create namespace airbyte
```

### Configure Kubernetes Secrets

Sensitive credentials such as AWS access keys are required to be made available in Kubernetes Secrets during deployment. The Kubernetes secret store and secret keys are referenced in your `values.yaml` file. Ensure all required secrets are configured before deploying Airbyte Self-Managed Enterprise.

You may apply your Kubernetes secrets by applying the example manifests below to your cluster, or using `kubectl` directly. If your Kubernetes cluster already has permissions to make requests to an external entity via an instance profile, credentials are not required. For example, if your Amazon EKS cluster has been assigned a sufficient AWS IAM role to make requests to AWS S3, you do not need to specify access keys.

#### Creating a Kubernetes Secret

While you can set the name of the secret to whatever you prefer, you will need to set that name in various places in your values.yaml file. For this reason we suggest that you keep the name of `airbyte-config-secrets` unless you have a reason to change it.

<details>
<summary>airbyte-config-secrets</summary>

<Tabs>
<TabItem value="S3" label="S3" default>

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  # Enterprise License Key
  license-key: ## e.g. xxxxx.yyyyy.zzzzz

  # Database Secrets
  database-host: ## e.g. database.internal
  database-port: ## e.g. 5432
  database-name: ## e.g. airbyte
  database-user: ## e.g. airbyte
  database-password: ## e.g. password

  # Instance Admin
  instance-admin-email: ## e.g. admin@company.example
  instance-admin-password: ## e.g. password

  # SSO OIDC Credentials
  client-id: ## e.g. e83bbc57-1991-417f-8203-3affb47636cf
  client-secret: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

  # AWS S3 Secrets
  s3-access-key-id: ## e.g. AKIAIOSFODNN7EXAMPLE
  s3-secret-access-key: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

  # Azure Blob Storage Secrets
  azure-blob-store-connection-string: ## DefaultEndpointsProtocol=https;AccountName=azureintegration;AccountKey=wJalrXUtnFEMI/wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY/wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY==;EndpointSuffix=core.windows.net

  # AWS Secret Manager
  aws-secret-manager-access-key-id: ## e.g. AKIAIOSFODNN7EXAMPLE
  aws-secret-manager-secret-access-key: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

  # Azure Secret Manager
  azure-key-vault-client-id: ## 3fc863e9-4740-4871-bdd4-456903a04d4e
  azure-key-vault-client-secret: ## KWP6egqixiQeQoKqFZuZq2weRbYoVxMH

```

You can also use `kubectl` to create the secret directly from the CLI:

```sh
kubectl create secret generic airbyte-config-secrets \
  --from-literal=license-key='' \
  --from-literal=database-host='' \
  --from-literal=database-port='' \
  --from-literal=database-name='' \
  --from-literal=database-user='' \
  --from-literal=database-password='' \
  --from-literal=instance-admin-email='' \
  --from-literal=instance-admin-password='' \
  --from-literal=s3-access-key-id='' \
  --from-literal=s3-secret-access-key='' \
  --from-literal=aws-secret-manager-access-key-id='' \
  --from-literal=aws-secret-manager-secret-access-key='' \
  --namespace airbyte
```

</TabItem>
<TabItem value="GCS" label="GCS">

First, create a new file `gcp.json` containing the credentials JSON blob for the service account you are looking to assume.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  # Enterprise License Key
  license-key: ## e.g. xxxxx.yyyyy.zzzzz

  # Database Secrets
  database-host: ## e.g. database.internal
  database-port: ## e.g. 5432
  database-name: ## e.g. airbyte
  database-user: ## e.g. airbyte
  database-password: ## e.g. password

  # Instance Admin Credentials
  instance-admin-email: ## e.g. admin@company.example
  instance-admin-password: ## e.g. password

  # SSO OIDC Credentials
  client-id: ## e.g. e83bbc57-1991-417f-8203-3affb47636cf
  client-secret: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

  # GCP Secrets
  gcp.json: <CREDENTIALS_JSON_BLOB>
```

Using `kubectl` to create the secret directly from the `gcp.json` file:

```sh
kubectl create secret generic airbyte-config-secrets \
  --from-literal=license-key='' \
  --from-literal=database-host='' \
  --from-literal=database-port='' \
  --from-literal=database-name='' \
  --from-literal=database-user='' \
  --from-literal=database-password='' \
  --from-literal=instance-admin-email='' \
  --from-literal=instance-admin-password='' \
  --from-file=gcp.json
  --namespace airbyte
```

</TabItem>
</Tabs>
</details>

## Installation Steps

### Step 1: Add Airbyte Helm Repository

Follow these instructions to add the Airbyte helm repository:

1. Run `helm repo add airbyte https://airbytehq.github.io/helm-charts`, where `airbyte` is the name of the repository that will be indexed locally.
2. Perform the repo indexing process, and ensure your helm repository is up-to-date by running `helm repo update`.
3. You can then browse all charts uploaded to your repository by running `helm search repo airbyte`.

### Step 2: Configure your Deployment

1. Inside your `airbyte` directory, create an empty `values.yaml` file.

2. Paste the following into your newly created `values.yaml` file. This is required to deploy Airbyte Self-Managed Enterprise:

    ```yaml title="values.yaml"
    global:
      edition: enterprise
    ```

3. To enable SSO authentication, add instance admin details [SSO auth details](/platform/access-management/sso) to your `values.yaml` file, under `global`. See the [following guide](/platform/access-management/sso#set-up) on how to collect this information for various IDPs, such as Okta and Azure Entra ID.

    <Tabs groupId="helm-chart-version">
    <TabItem value='helm-1' label='Helm chart V1' default>

    ```yaml title="values.yaml"
    auth:
      instanceAdmin:
        firstName: ## First name of admin user.
        lastName: ## Last name of admin user.
      identityProvider:
        type: oidc
        secretName: airbyte-config-secrets ## Name of your Kubernetes secret.
        oidc:
          domain: ## e.g. company.example
          appName: ## e.g. airbyte
          display-name: ## e.g. Company SSO - optional, falls back to appName if not provided
          clientIdSecretKey: client-id
          clientSecretSecretKey: client-secret
    ```

    </TabItem>
    <TabItem value='helm-2' label='Helm chart V2 with OIDC' default>

    ```yaml title="values.yaml"
    global:
      auth:
      
        # -- Admin user configuration
        instanceAdmin:
          firstName: ""
          lastName:  ""
          emailSecretKey: "" # The key within `emailSecretName` where the initial user's email is stored
          passwordSecretKey: "" # The key within `passwordSecretName` where the initial user's password is stored

        # -- SSO Identify Provider configuration; (requires Enterprise)
        identityProvider:
            secretName: "" # Secret name where the OIDC configuration is stored
            type: "oidc"
            oidc:
              # -- OIDC application domain
              domain: ""
              # -- OIDC application name
              appName: ""
              # -- The key within `clientIdSecretName` where the OIDC client id is stored
              clientIdSecretKey: ""
              # -- The key within `clientSecretSecretName` where the OIDC client secret is stored
              clientSecretSecretKey: ""
    ```

    </TabItem>
    <TabItem value='helm-2-oidc' label='Helm chart V2 with generic OIDC' default>

    ```yaml title="values.yaml"
    global:
      auth:
      
        # -- Admin user configuration
        instanceAdmin:
          firstName: ""
          lastName:  ""
          emailSecretKey: "" # The key within `emailSecretName` where the initial user's email is stored
          passwordSecretKey: "" # The key within `passwordSecretName` where the initial user's password is stored

        # -- SSO Identify Provider configuration; (requires Enterprise)
        identityProvider:
            secretName: "" # Secret name where the OIDC configuration is stored
            type: "generic-oidc"
            genericOidc:
              clientId: ""
              audience: ""
              extraScopes: ""
              issuer: ""
              endpoints:
                authorizationServerEndpoint: ""
                jwksEndpoint: ""
              fields:
                subject: sub
                email: email
                name: name
                issuer: iss
    ```

    </TabItem>
    </Tabs>

4. You must configure the public facing URL of your Airbyte instance to your `values.yaml` file, under `global`:

    <Tabs groupId="helm-chart-version">
    <TabItem value='helm-1' label='Helm chart V1' default>

    ```yaml title="values.yaml"
    global:
      airbyteUrl: # e.g. https://airbyte.company.example
    ```

    </TabItem>
    <TabItem value='helm-2' label='Helm chart V2' default>

    ```yaml title="values.yaml"
    global:
      airbyteUrl: # e.g. https://airbyte.company.example
    ```

    </TabItem>
    </Tabs>

5. Verify the configuration of your `values.yaml` so far. Ensure `license-key`, `instance-admin-email` and `instance-admin-password` are all available via Kubernetes Secrets (configured in [prerequisites](#creating-a-kubernetes-secret)). It should appear as follows:

<details>
<summary>Sample initial values.yaml file</summary>

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml
global:
  edition: enterprise
  airbyteUrl: # e.g. https://airbyte.company.example
  auth:
    instanceAdmin:
      firstName: ## First name of admin user.
      lastName: ## Last name of admin user.
    identityProvider:
      type: oidc
      secretName: airbyte-config-secrets ## Name of your Kubernetes secret.
      oidc:
        domain: ## e.g. company.example
        appName: ## e.g. airbyte
        clientIdSecretKey: client-id
        clientSecretSecretKey: client-secret
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml
global:
  edition: enterprise
  airbyteUrl: # e.g. https://airbyte.company.example
  auth:
    instanceAdmin:
      firstName: ## First name of admin user.
      lastName: ## Last name of admin user.
    identityProvider:
      type: oidc
      secretName: airbyte-config-secrets ## Name of your Kubernetes secret.
      oidc:
        domain: ## e.g. company.example
        appName: ## e.g. airbyte
        clientIdSecretKey: client-id
        clientSecretSecretKey: client-secret
```

</TabItem>
</Tabs>

</details>

The following subsections help you customize your deployment to use an external database, log storage, dedicated ingress, and more. To skip this and deploy a minimal, local version of Self-Managed Enterprise, [jump to Step 3](#step-3-deploy-self-managed-enterprise).

#### Configuring the Airbyte Database

For Self-Managed Enterprise deployments, you must use a dedicated database instance for better reliability and backups, such as AWS RDS or GCP Cloud SQL. Don't use the default internal Postgres database, `airbyte/db`, that Airbyte spins up within the Kubernetes cluster.

We assume in the following that you've already configured a Postgres instance:

<details>
<summary>External database setup steps</summary>

Add external database details to your `values.yaml` file. This disables the default internal Postgres database (`airbyte/db`), and configures the external Postgres database. You can override all of the values below by setting them in the airbyte-config-secrets or set them directly here. You must set the database password in the airbyte-config-secrets. Here is an example configuration:

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml
postgresql:
  enabled: false

global:
  database:
    # -- Secret name where database credentials are stored
    secretName: "" # e.g. "airbyte-config-secrets"

    # -- The database host
    host: ""
    # -- The key within `secretName` where host is stored 
    #hostSecretKey: "" # e.g. "database-host"

    # -- The database port
    port: ""
    # -- The key within `secretName` where port is stored 
    #portSecretKey: "" # e.g. "database-port" 

    # -- The database name
    database: ""
    # -- The key within `secretName` where the database name is stored 
    #databaseSecretKey: "" # e.g. "database-name" 

    # -- The database user
    user: "" # -- The key within `secretName` where the user is stored 
    #userSecretKey: "" # e.g. "database-user"

    # -- The key within `secretName` where password is stored
    passwordSecretKey: "" # e.g."database-password"
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
postgresql:
  enabled: false

global: 
  database:
    # -- Secret name where database credentials are stored
    secretName: "" # e.g. "airbyte-config-secrets"
    # -- The database host
    host: ""
    # -- The database port
    port:
    # -- The database name - this key used to be "database" in Helm chart 1.0
    name: ""

    # Use EITHER user or userSecretKey, but not both
    # -- The database user
    user: ""
    # -- The key within `secretName` where the user is stored
    userSecretKey: "" # e.g. "database-user"

    # Use EITHER password or passwordSecretKey, but not both
    # -- The database password
    password: ""
    # -- The key within `secretName` where the password is stored
    passwordSecretKey: "" # e.g."database-password"
```

</TabItem>
</Tabs>

</details>

#### Configuring External Logging

For Self-Managed Enterprise deployments, spin up standalone log storage for additional reliability using tools such as S3 and GCS. Don't use the default internal MinIO storage, `airbyte/minio`. It's then a common practice to configure additional log forwarding from external log storage into your observability tool.

<details>
<summary>External log storage setup steps</summary>

Add external log storage details to your `values.yaml` file. This disables the default internal Minio instance (`airbyte/minio`), and configures the external log database:

<Tabs>
<TabItem value="S3" label="S3" default>

Ensure you've already created a Kubernetes secret containing both your S3 access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `aws-s3-access-key-id` and `aws-s3-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
global:
  storage:
    type: "S3"
    storageSecretName: airbyte-config-secrets # Name of your Kubernetes secret.
    bucket: ## S3 bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    s3:
      region: "" ## e.g. us-east-1
      authenticationType: credentials ## Use "credentials" or "instanceProfile"
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
global:
  storage:
    secretName: ""
    type: minio # default storage is minio. Set to s3, gcs, or azure, according to what you use.

    bucket:
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
      activityPayload: airbyte-bucket
    s3:
      region: "" ## e.g. us-east-1
      authenticationType: credentials ## Use "credentials" or "instanceProfile"
      accessKeyId: ""
      secretAccessKey: ""
```

</TabItem>
</Tabs>

Set `authenticationType` to `instanceProfile` if the compute infrastructure running Airbyte has pre-existing permissions (e.g. IAM role) to read and write from the appropriate buckets.

</TabItem>
<TabItem value="GCS" label="GCS" default>

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
global:
  storage:
    type: "GCS"
    storageSecretName: airbyte-config-secrets
    bucket: ## GCS bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    gcs:
      projectId: <project-id>
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
global:
  storage:
    secretName: ""
    type: minio # default storage is minio. Set to s3, gcs, or azure, according to what you use.
    bucket:
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
      activityPayload: airbyte-bucket
    gcs:
      projectId: <project-id>
      credentialsJson:  <base64-encoded>
      credentialsJsonPath: /secrets/gcs-log-creds/gcp.json
```

</TabItem>
</Tabs>

</TabItem>

<TabItem value="Azure Blob" label="Azure" default>

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
global:
  storage:
    type: "Azure"
    storageSecretName: airbyte-config-secrets # Name of your Kubernetes secret.
    bucket: ## S3 bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    azure:
      connectionStringSecretKey: azure-blob-store-connection-string
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
global:
  storage:
    secretName: ""
    type: minio # default storage is minio. Set to s3, gcs, or azure, according to what you use.
    bucket:
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
      activityPayload: airbyte-bucket
    azure:
      # one of the following: connectionString, connectionStringSecretKey
      connectionString: <azure storage connection string>
      connectionStringSecretKey: <secret coordinate containing an existing connection-string secret>
```

</TabItem>
</Tabs>

</TabItem>
</Tabs>

</details>

#### Configuring External Connector Secret Management

Airbyte's default behavior is to store encrypted connector secrets on your cluster as Kubernetes secrets. You may <b>optionally</b> opt to instead store connector secrets in an external secret manager such as AWS Secrets Manager, Google Secrets Manager or Hashicorp Vault. Upon creating a new connector, secrets (e.g. OAuth tokens, database passwords) will be written to, then read from the configured secrets manager.

<details>
<summary>Configuring external connector secret management</summary>

**Modifying the configuration of connector secret storage will cause all existing connectors to fail**. You will need to recreate these connectors to ensure they are reading from the appropriate secret store.

<Tabs>
<TabItem label="Amazon" value="Amazon">

If authenticating with credentials, ensure you've already created a Kubernetes secret containing both your AWS Secrets Manager access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `aws-secret-manager-access-key-id` and `aws-secret-manager-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
secretsManager:
  type: awsSecretManager
  awsSecretManager:
    region: <aws-region>
    authenticationType: credentials ## Use "credentials" or "instanceProfile"
    tags: ## Optional - You may add tags to new secrets created by Airbyte.
      - key: ## e.g. team
        value: ## e.g. deployments
      - key: business-unit
        value: engineering
    kms: ## Optional - ARN for KMS Decryption.
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
global:
  secretsManager:
    enabled: false
    type: AWS_SECRET_MANAGER
    secretName: "airbyte-config-secrets"
    # Set ONE OF the following groups of configurations, based on your configuration in global.secretsManager.type.
    awsSecretManager:
      region: <aws-region>
      authenticationType: credentials ## Use "credentials" or "instanceProfile"
      tags: ## Optional - You may add tags to new secrets created by Airbyte.
      - key: ## e.g. team
          value: ## e.g. deployments
        - key: business-unit
          value: engineering
      kms: ## Optional - ARN for KMS Decryption.
```

</TabItem>
</Tabs>

Set `authenticationType` to `instanceProfile` if the compute infrastructure running Airbyte has pre-existing permissions (e.g. IAM role) to read and write from AWS Secrets Manager.

To decrypt secrets in the secret manager with AWS KMS, configure the `kms` field, and ensure your Kubernetes cluster has pre-existing permissions to read and decrypt secrets.

</TabItem>
<TabItem label="GCP" value="GCP">

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `gcp-cred-secrets` Kubernetes secret, under a `gcp.json` file. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets). For simplicity, we recommend provisioning a single service account with access to both GCS and GSM.

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
secretsManager:
  type: googleSecretManager
  storageSecretName: gcp-cred-secrets
  googleSecretManager:
    projectId: <project-id>
    credentialsSecretKey: gcp.json
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
global:
  secretsManager:
    enabled: false
    type: GOOGLE_SECRET_MANAGER
    secretName: gcp-cred-secrets
    googleSecretManager:
      projectId: <project-id>
      credentialsSecretKey: gcp.json
```

</TabItem>
</Tabs>

</TabItem>

<TabItem label="Azure Key Vault" value="Azure">

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
global:
  secretsManager:
    type: azureKeyVault
    azureKeyVault:
      vaultUrl: ## https://my-vault.vault.azure.net/
      tenantId: ## 3fc863e9-4740-4871-bdd4-456903a04d4e
      tags: ## Optional - You may add tags to new secrets created by Airbyte.
        - key: ## e.g. team
          value: ## e.g. deployments
        - key: business-unit
          value: engineering
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
global:
  secretsManager:
    enabled: true
    type: AZURE_KEY_VAULT
    secretName: "airbyte-config-secrets"
    azureKeyVault:
      tenantId: ""
      vaultUrl: ""
      clientId: ""
      clientIdSecretKey: ""
      clientSecret: ""
      clientSecretSecretKey: ""
      tags: ""
```

</TabItem>
</Tabs>

</TabItem>
</Tabs>

</details>

#### Configuring Ingress

To access the Airbyte UI, you need to configure ingress for your deployment. You have two options:

- **Use Airbyte's Helm chart ingress configuration** - Configure ingress through your `values.yaml` file.

- **Bring your own ingress** - Manually create and manage your own Kubernetes ingress resource.

Use the Helm chart ingress configuration if you want Airbyte to manage ingress creation and updates automatically. Use your own ingress if you need custom ingress configurations beyond what the Helm chart provides, or if you prefer to manage ingress independently.

##### Before enabling ingress

You must have an ingress controller deployed in your Kubernetes cluster. Refer to ingress controller documentation for setup: [NGINX](https://kubernetes.github.io/ingress-nginx/deploy/), [AWS ALB](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html), or your controller's documentation. For TLS certificate management, refer to [cert-manager](https://cert-manager.io/docs/) or your cloud provider's certificate service.

Set appropriate backend timeout values for the Airbyte server ingress. Timeout values that are too short can lead to 504 errors in the UI when creating new sources or destinations.

##### Set up ingress in Airbyte

<details>
<summary>Option 1: use Airbyte's Helm chart ingress configuration</summary>

:::note
**Helm V2 users:** Follow the configuration examples below.

**Helm V1 users:** Ingress is available but uses a different configuration format. See the [values.yaml reference](/platform/deploying-airbyte/values) for the V1 ingress configuration structure.
:::

You can configure ingress directly in your `values.yaml` file. Airbyte automatically creates and manages the ingress resource for you.

```yaml
ingress:
  enabled: true
  className: "nginx"  # Specify your ingress class
  annotations: {}
    # Add any ingress-specific annotations here
  hosts:
    - host: airbyte.example.com  # Replace with your domain
      paths:
        - path: /auth
          pathType: Prefix
          backend: keycloak  # For Keycloak authentication (if using OIDC)
        - path: /
          pathType: Prefix
          backend: server  # Routes to airbyte-server
        - path: /connector-builder
          pathType: Prefix
          backend: connector-builder-server  # Required for connector builder
  tls: []
    # Optionally configure TLS
    # - secretName: airbyte-tls
    #   hosts:
    #     - airbyte.example.com
```

The `backend` field specifies which service to route to:

- `keycloak` - Routes to Keycloak service (required for OIDC authentication, omit if using generic OIDC)
- `server` - Routes to the main Airbyte server
- `connector-builder-server` - Routes to the connector builder service (required for Airbyte's connector builder to work)

</details>

<details>
<summary>Option 2: bring your own ingress</summary>

If you prefer to manage your own ingress resource, you can manually create a Kubernetes ingress resource.

<Tabs>
<TabItem value="NGINX" label="NGINX">

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: # ingress name, example: enterprise-demo
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
    - host: airbyte.example.com # replace with your host
      http:
        paths:
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-keycloak-svc 
                name: airbyte-enterprise-airbyte-keycloak-svc 
                port: 
                  number: 8180 
            path: /auth
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-connector-builder-server-svc
                name: airbyte-enterprise-airbyte-connector-builder-server-svc
                port:
                  number: 80 # service port, example: 8080
            path: /api/v1/connector_builder/
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-server-svc
                name: airbyte-enterprise-airbyte-server-svc
                port:
                  number: 8001 # service port, example: 8080
            path: /
            pathType: Prefix
```

</TabItem>
<TabItem value="Amazon ALB" label="Amazon ALB">

If you are intending on using Amazon Application Load Balancer (ALB) for ingress, this ingress definition will be close to what's needed to get up and running:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airbyte-ingress # ingress name, e.g. airbyte-production-ingress
  annotations:
    # Specifies that the Ingress should use an AWS ALB.
    kubernetes.io/ingress.class: "alb"
    # Redirects HTTP traffic to HTTPS.
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    # Creates an internal ALB, which is only accessible within your VPC or through a VPN.
    alb.ingress.kubernetes.io/scheme: internal
    # Specifies the ARN of the SSL certificate managed by AWS ACM, essential for HTTPS.
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-x:xxxxxxxxx:certificate/xxxxxxxxx-xxxxx-xxxx-xxxx-xxxxxxxxxxx
    # Sets the idle timeout value for the ALB.
    alb.ingress.kubernetes.io/load-balancer-attributes: idle_timeout.timeout_seconds=30
    # [If Applicable] Specifies the VPC subnets and security groups for the ALB
    # alb.ingress.kubernetes.io/subnets: '' e.g. 'subnet-12345, subnet-67890'
    # alb.ingress.kubernetes.io/security-groups: <SECURITY_GROUP>
spec:
  rules:
    - host: airbyte.example.com # replace with your host
      http:
        paths:
          - backend:
              service:
                name: airbyte-enterprise-airbyte-keycloak-svc
                port:
                  number: 8180
            path: /auth
            pathType: Prefix
          - backend:
              service:
                name: airbyte-enterprise-airbyte-connector-builder-server-svc
                port:
                  number: 80
            path: /api/v1/connector_builder/
            pathType: Prefix
          - backend:
              service:
                name: airbyte-enterprise-airbyte-server-svc
                port:
                  number: 8001
            path: /
            pathType: Prefix
```

The ALB controller will use a `ServiceAccount` that requires the [following IAM policy](https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json) to be attached.

</TabItem>
</Tabs>

</details>

##### Ensure your airbyte URL matches your ingress host

Once you configure ingress, ensure that the value of `global.airbyteUrl` in your values.yaml matches the ingress URL.

```yaml
global:
  airbyteUrl: # e.g. https://airbyte.example.com
```

You may configure ingress using a load balancer or an API Gateway. We do not currently support most service meshes (such as Istio). If you are having networking issues after fully deploying Airbyte, please verify that firewalls or lacking permissions are not interfering with pod-pod communication. Please also verify that deployed pods have the right permissions to make requests to your external database.

### Step 3: Deploy Self-Managed Enterprise

Install Airbyte Self-Managed Enterprise on helm using the following command:

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```bash
helm install airbyte-enterprise airbyte/airbyte \
  --namespace airbyte \   # Target Kubernetes namespace
  --values ./values.yaml  # Custom configuration values
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

1. Identify the Helm chart version that corresponds to the platform version you want to run. Most Helm chart versions are designed to work with one Airbyte version, and they don't necessarily have the same version number.

    ```bash
    helm search repo airbyte-v2 --versions
    ```

    You should see something like this:

    ```text
    NAME                            CHART VERSION   APP VERSION     DESCRIPTION
    airbyte-v2/airbyte              2.0.18          2.0.0           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.17          1.8.5           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.16          1.8.4           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.15          1.8.4           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.14          1.8.4           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.13          1.8.3           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.12          1.8.2           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.11          1.8.2           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.10          1.8.1           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.9           1.8.0           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.8           1.8.0           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.7           1.7.1           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.6           1.7.1           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.5           1.7.0           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.4           1.6.3           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.3           1.6.2           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.2           1.6.2           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.1           1.6.1           Helm chart to deploy airbyte
    airbyte-v2/airbyte              2.0.0           1.6.0           Helm chart to deploy airbyte
    airbyte-v2/airbyte-data-plane   2.0.0           2.0.0           A Helm chart for installing an Airbyte Data Plane.
    ```

2. Install Airbyte into your Helm chart V2 namespace. In this example, you install Airbyte version 2.0.

    ```bash
    helm install airbyte airbyte-v2/airbyte \
      --namespace airbyte-v2 \       # Target Kubernetes namespace
      --values ./values.yaml \       # Custom configuration values
      --version 2.0.18               # Helm chart version to use
    ```

</TabItem>
</Tabs>

To uninstall Self-Managed Enterprise, run `helm uninstall airbyte-enterprise`.

## Updating Self-Managed Enterprise

Upgrade Airbyte Self-Managed Enterprise by:

1. Running `helm repo update`. This pulls an up-to-date version of our helm charts, which is tied to a version of the Airbyte platform.
2. Re-installing Airbyte Self-Managed Enterprise:

    <Tabs groupId="helm-chart-version">
    <TabItem value='helm-1' label='Helm chart V1' default>

    ```bash
    helm upgrade airbyte-enterprise airbyte/airbyte \
      --namespace airbyte \   # Target Kubernetes namespace
      --values ./values.yaml  # Custom configuration values
    ```

    </TabItem>
    <TabItem value='helm-2' label='Helm chart V2' default>

    ```bash
    helm upgrade airbyte airbyte-v2/airbyte \
      --namespace airbyte-v2 \       # Target Kubernetes namespace
      --values ./values.yaml \       # Custom configuration values
      --version 2.x.x                # Helm chart version to use
    ```

    </TabItem>
    </Tabs>

## Customizing your Deployment

In order to customize your deployment, you need to create an additional `values.yaml` file in your `airbyte` directory, and populate it with configuration override values. A thorough `values.yaml` example including many configurations can be located in [Values.yaml reference](../deploying-airbyte/values) folder of the Airbyte repository.

After specifying your own configuration, run the following command:

<Tabs groupId="helm-chart-version">
    <TabItem value='helm-1' label='Helm chart V1' default>

    ```bash
    helm upgrade airbyte-enterprise airbyte/airbyte \
      --namespace airbyte \   # Target Kubernetes namespace
      --values ./values.yaml  # Custom configuration values
    ```

    </TabItem>
    <TabItem value='helm-2' label='Helm chart V2' default>

    ```bash
    helm upgrade airbyte-enterprise airbyte-v2/airbyte \
      --namespace airbyte-v2 \       # Target Kubernetes namespace
      --values ./values.yaml \       # Custom configuration values
      --version 2.x.x                # Helm chart version to use
    ```

    </TabItem>
    </Tabs>

### Configure a custom image registry

You can optionally configure Airbyte to pull Docker images from a custom image registry rather than [Airbyte's public Docker repository](https://hub.docker.com/u/airbyte). In this case, Airbyte pulls both platform images (e.g. `server`, `workload-launcher`, etc.) and connector images (e.g. Postgres Source, S3 Destination, etc.) from the configured registry.

Implementing Airbyte this way has several advantages.

- **Security**: Private custom image registries keep images in your network, reducing the risk of external threats.
- **Access control**: You have more control over who can access and modify images.
- **Compliance**: By keeping images in a controlled environment, it's easier to prove compliance with regulatory requirements for data storage and handling.

[Custom Docker connectors](../operator-guides/using-custom-connectors/) in your workspace that specify an image using a fully qualified domain name (for example, `example.com/airbyte/your-custom-source`) ignore your configured custom image registry and pull images from the domain specified by that connector.

<details>
<summary>Before you start</summary>

1. Set up your custom image registry. The examples in this article use GitHub, but you have many options. Here are some popular ones:

    <ContainerProviders/>

2. Install `abctl`. Although abctl is typically only used to manage local installations of Airbyte, it has some helpful commands for this process.

    <Tabs>
      <TabItem value="abctl-brew" label="Homebrew" default>
        ```bash
        brew tap airbytehq/tap
        brew install abctl
        ```
      </TabItem>
      <TabItem value="abctl-go" label="Go">
        ```bash
        go install github.com/airbytehq/abctl@latest
        ```
      </TabItem>
      <TabItem value="abctl-gh" label="GitHub">
        See [GitHub releases](https://github.com/airbytehq/abctl/releases/latest).
      </TabItem>
    </Tabs>

</details>

<details>
<summary>Get a list of all Airbyte images</summary>

To get a list of Airbyte images for the latest version, use abctl.

```bash
abctl images manifest
```

You should see something like this:

```bash
airbyte/bootloader:1.8.0
airbyte/connector-builder-server:1.8.0
airbyte/connector-sidecar:1.8.0
airbyte/container-orchestrator:1.8.0
airbyte/cron:1.8.0
airbyte/db:1.8.0
airbyte/mc:latest
airbyte/server:1.8.0
airbyte/worker:1.8.0
airbyte/workload-api-server:1.8.0
airbyte/workload-init-container:1.8.0
airbyte/workload-launcher:1.8.0
bitnami/kubectl:1.28.9
busybox:1.35
busybox:latest
curlimages/curl:8.1.1
minio/minio:RELEASE.2023-11-20T22-40-07Z
temporalio/auto-setup:1.23.0
```

</details>

<details>
<summary>Step 1: Customize Airbyte to use your image registry</summary>

To pull all platform and connector images from a custom image registry, add the following customization to Airbyte's `values.yaml` file, replacing the `registry` value with your own registry location.

```yaml title="values.yaml"
global:
  image:
    registry: ghcr.io/NAMESPACE
```

If your registry requires authentication, you can create a Kubernetes secret and reference it in the Airbyte config:

1. Create a Kubernetes secret. In this example, you create a secret called `regcred` from a config file. That file contains authentication information for a private custom image registry. [Learn more about Kubernetes secrets](https://kubernetes.io/docs/tasks/configmap-secret/).

    ```bash
    kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson
    ```

2. Add the secret you created to your `values.yaml` file. In this example, you use your `regcred` secret to authenticate.

    ```yaml title="values.yaml"
    global:
      image:
        registry: ghcr.io/NAMESPACE
      // highlight-start
      imagePullSecrets:
        - name: regcred
      // highlight-end
    ```

</details>

<details>
<summary>Step 2: Tag and push Airbyte images</summary>

Tag and push Airbyte's images to your custom image registry.

In this example, you tag all platform images and push them all to GitHub.

```bash
abctl images manifest | xargs -L1 -I{} docker tag {} ghcr.io/NAMESPACE/{} && docker push ghcr.io/NAMESPACE/{}
```

You can also pull Airbyte's connector images from Docker, tag them, and push them to your custom image registry. You must do this prior to adding a source or destination.

In this example, you pull a connector from Docker, tag it, and push it to GitHub.

```bash
docker pull airbyte/destination-google-sheets:latest
docker tag airbyte/desination-google-sheets:latest ghcr.io/NAMESPACE/desination-google-sheets:latest
docker push ghcr.io/NAMESPACE/destination-google-sheets:latest    
```

Now, when you install Airbyte, images will come from the custom image registry you configured.

</details>

### Customizing your Service Account

You may choose to use your own service account instead of the Airbyte default, `airbyte-sa`. This may allow for better audit trails and resource management specific to your organizational policies and requirements.

To do this, add the following to your `values.yaml`:

```
serviceAccount:
  name:
```

### Deploying to multiple regions

See [Multiple region deployments](multi-region).

### Enabling audit logs

See [Audit logging](audit-logging.md).

## AWS Policies Appendix

Ensure your access key is tied to an IAM user or you are using a Role with the following policies.

### AWS S3 Policy

The [following policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html#iam-policy-ex0), allow the cluster to communicate with  S3 storage

```yaml
{
  "Version": "2012-10-17",
  "Statement":
    [
      { "Effect": "Allow", "Action": "s3:ListAllMyBuckets", "Resource": "*" },
      {
        "Effect": "Allow",
        "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
        "Resource": "arn:aws:s3:::YOUR-S3-BUCKET-NAME"
      },
      {
        "Effect": "Allow",
        "Action":
          [
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:GetObject",
            "s3:GetObjectAcl",
            "s3:DeleteObject"
          ],
        "Resource": "arn:aws:s3:::YOUR-S3-BUCKET-NAME/*"
      }
    ]
}
```

### AWS Secret Manager Policy

```yaml
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:CreateSecret",
                "secretsmanager:ListSecrets",
                "secretsmanager:DescribeSecret",
                "secretsmanager:TagResource",
                "secretsmanager:UpdateSecret"
            ],
            "Resource": [
                "*"
            ],
            "Condition": {
                "ForAllValues:StringEquals": {
                    "secretsmanager:ResourceTag/AirbyteManaged": "true"
                }
            }
        }
    ]
}
```

## Azure Policies Appendix

### Azure Key Vault Policy

Airbyte requires the ability to write and read secrets in an Azure Key Vault. The built-in role that supports this is the Key Vault Secrets Officer role, whose JSON configuration can be viewed below to understand the specific permissions needed.

```yaml
{
    "id": "/providers/Microsoft.Authorization/roleDefinitions/b86a8fe4-44ce-4948-aee5-eccb2c155cd7",
    "properties": {
        "roleName": "Key Vault Secrets Officer",
        "description": "Perform any action on the secrets of a key vault, except manage permissions. Only works for key vaults that use the 'Azure role-based access control' permission model.",
        "assignableScopes": [
            "/"
        ],
        "permissions": [
            {
                "actions": [
                    "Microsoft.Authorization/*/read",
                    "Microsoft.Insights/alertRules/*",
                    "Microsoft.Resources/deployments/*",
                    "Microsoft.Resources/subscriptions/resourceGroups/read",
                    "Microsoft.Support/*",
                    "Microsoft.KeyVault/checkNameAvailability/read",
                    "Microsoft.KeyVault/deletedVaults/read",
                    "Microsoft.KeyVault/locations/*/read",
                    "Microsoft.KeyVault/vaults/*/read",
                    "Microsoft.KeyVault/operations/read"
                ],
                "notActions": [],
                "dataActions": [
                    "Microsoft.KeyVault/vaults/secrets/*"
                ],
                "notDataActions": []
            }
        ]
    }
}
```
