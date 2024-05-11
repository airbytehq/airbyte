---
products: oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Implementation Guide

[Airbyte Self-Managed Enterprise](./README.md) is in an early access stage for select priority users. Once you [are qualified for a Self-Managed Enterprise license key](https://airbyte.com/company/talk-to-sales), you can deploy Airbyte with the following instructions.

Airbyte Self-Managed Enterprise must be deployed using Kubernetes. This is to enable Airbyte's best performance and scale. The core components \(api server, scheduler, etc\) run as deployments while the scheduler launches connector-related pods on different nodes.

## Prerequisites

### Infrastructure Prerequisites

For a production-ready deployment of Self-Managed Enterprise, various infrastructure components are required. We recommend deploying to Amazon EKS or Google Kubernetes Engine. The following diagram illustrates a typical Airbyte deployment running on AWS:

![AWS Architecture Diagram](./assets/self-managed-enterprise-aws.png)

Prior to deploying Self-Managed Enterprise, we recommend having each of the following infrastructure components ready to go. When possible, it's easiest to have all components running in the same [VPC](https://docs.aws.amazon.com/eks/latest/userguide/network_reqs.html). The provided recommendations are for customers deploying to AWS:

| Component                | Recommendation                                                                                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kubernetes Cluster       | Amazon EKS cluster running in [2 or more availability zones](https://docs.aws.amazon.com/eks/latest/userguide/disaster-recovery-resiliency.html) on a minimum of 6 nodes. |
| Ingress                  | [Amazon ALB](#configuring-ingress) and a URL for users to access the Airbyte UI or make API requests.                                                                     |
| Object Storage           | [Amazon S3 bucket](#configuring-external-logging) with two directories for log and state storage.                                                                         |
| Dedicated Database       | [Amazon RDS Postgres](#configuring-the-airbyte-database) with at least one read replica.                                                                                  |
| External Secrets Manager | [Amazon Secrets Manager](/operator-guides/configuring-airbyte#secrets) for storing connector secrets.                                                                     |

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

Sensitive credentials such as AWS access keys are required to be made available in Kubernetes Secrets during deployment. The Kubernetes secret store and secret keys are referenced in your `values.yml` file. Ensure all required secrets are configured before deploying Airbyte Self-Managed Enterprise.

You may apply your Kubernetes secrets by applying the example manifests below to your cluster, or using `kubectl` directly. If your Kubernetes cluster already has permissions to make requests to an external entity via an instance profile, credentials are not required. For example, if your Amazon EKS cluster has been assigned a sufficient AWS IAM role to make requests to AWS S3, you do not need to specify access keys.

#### External Log Storage

For Self-Managed Enterprise deployments, we recommend spinning up standalone log storage for additional reliability using tools such as S3 and GCS instead of against using the default internal Minio storage (`airbyte/minio`).

<details>
<summary>Secrets for External Log Storage</summary>

<Tabs>
<TabItem value="S3" label="S3" default>

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  ## Storage Secrets
  # S3
  s3-access-key-id: ## e.g. AKIAIOSFODNN7EXAMPLE
  s3-secret-access-key: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Overriding `name`, `s3-access-key-id` or `s3-secret-access-key` allows you to store these secrets in the location of your choice. If you do this, you will also need to specify the secret location in the bucket config for your `values.yml` file.

Using `kubectl` to create the secret directly:

```sh
kubectl create secret generic airbyte-config-secrets \
  --from-literal=s3-access-key-id='' \
  --from-literal=s3-secret-access-key='' \
  --namespace airbyte
```

Ensure your access key is tied to an IAM user with the [following policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html#iam-policy-ex0), allowing the cluster to S3 storage:

```yaml
{
  "Version": "2012-10-17",
  "Statement":
    [
      { "Effect": "Allow", "Action": "s3:ListAllMyBuckets", "Resource": "*" },
      {
        "Effect": "Allow",
        "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
        "Resource": "arn:aws:s3:::YOUR-S3-BUCKET-NAME",
      },
      {
        "Effect": "Allow",
        "Action":
          [
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:GetObject",
            "s3:GetObjectAcl",
            "s3:DeleteObject",
          ],
        "Resource": "arn:aws:s3:::YOUR-S3-BUCKET-NAME/*",
      },
    ],
}
```

</TabItem>
<TabItem value="GCS" label="GCS">

First, create a new file `gcp.json` containing the credentials JSON blob for the service account you are looking to assume.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gcp-cred-secrets
type: Opaque
stringData:
  gcp.json: <CREDENTIALS_JSON_BLOB>
```

Using `kubectl` to create the secret directly from the `gcp.json` file:

```sh
kubectl create secret generic gcp-cred-secrets --from-file=gcp.json --namespace airbyte
```

</TabItem>
</Tabs>
</details>

#### External Connector Secret Management

Airbyte's default behavior is to store encrypted connector secrets on your cluster as Kubernetes secrets. You may opt to instead store connector secrets in an external secret manager of your choosing (AWS Secrets Manager, Google Secrets Manager or Hashicorp Vault).

<details>
<summary>Secrets for External Connector Secret Management</summary>

To store connector secrets in AWS Secrets Manager via a manifest:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  aws-secret-manager-access-key-id: ## e.g. AKIAIOSFODNN7EXAMPLE
  aws-secret-manager-secret-access-key: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Overriding `name`, `aws-secret-manager-access-key-id` or `aws-secret-manager-secret-access-key` allows you to store these secrets in the location of your choice. If you do this, you will also need to specify the secret location in the secret manager config for your `values.yml` file.

Alternatively, you may choose to use `kubectl` to create the secret directly:

```sh
kubectl create secret generic airbyte-config-secrets \
  --from-literal=aws-secret-manager-access-key-id='' \
  --from-literal=aws-secret-manager-secret-access-key='' \
  --namespace airbyte
```

</details>

## Installation Steps

### Step 1: Add Airbyte Helm Repository

Follow these instructions to add the Airbyte helm repository:

1. Run `helm repo add airbyte https://airbytehq.github.io/helm-charts`, where `airbyte` is the name of the repository that will be indexed locally.
2. Perform the repo indexing process, and ensure your helm repository is up-to-date by running `helm repo update`.
3. You can then browse all charts uploaded to your repository by running `helm search repo airbyte`.

### Step 2: Create your Enterprise License File

1. Create a new `airbyte` directory. Inside, create an empty `airbyte.yml` file.

2. Paste the following into your newly created `airbyte.yml` file:

<details>
<summary>Template airbyte.yml file</summary>

```yaml
webapp-url: # example: http://localhost:8080

initial-user:
  email:
  first-name:
  last-name:
  username: # your existing Airbyte instance username
  password: # your existing Airbyte instance password

license-key: # license key provided by Airbyte team
```

</details>

3. Fill in the contents of the `initial-user` block. The credentials grant an initial user with admin permissions. You should store these credentials in a secure location.

4. Add your Airbyte Self-Managed Enterprise license key to your `airbyte.yml` in the `license-key` field.

5. To enable SSO authentication, add [SSO auth details](/access-management/sso) to your `airbyte.yml` file.

<details>
<summary>Configuring auth in your airbyte.yml file</summary>

<Tabs>
<TabItem value="Okta" label="Okta">
To configure SSO with Okta, add the following at the end of your `airbyte.yml` file:

```yaml
auth:
  identity-providers:
    - type: okta
      domain: $OKTA_DOMAIN
      app-name: $OKTA_APP_INTEGRATION_NAME
      client-id: $OKTA_CLIENT_ID
      client-secret: $OKTA_CLIENT_SECRET
```

See the [following guide](/access-management/sso-providers/okta) on how to collect this information for Okta.

</TabItem>
<TabItem value="Other" label="Other">

To configure SSO with any identity provider via [OpenID Connect (OIDC)](https://openid.net/developers/how-connect-works/), such as Azure Entra ID (formerly ActiveDirectory), add the following at the end of your `values.yml` file:

```yaml
auth:
  identity-providers:
    - type: oidc
      domain: $DOMAIN
      app-name: $APP_INTEGRATION_NAME
      client-id: $CLIENT_ID
      client-secret: $CLIENT_SECRET
```

See the [following guide](/access-management/sso-providers/azure-entra-id) on how to collect this information for Azure Entra ID (formerly ActiveDirectory).

</TabItem>
</Tabs>

To modify auth configurations on an existing deployment (after Airbyte has been installed at least once), you will need to `helm upgrade` Airbyte with the additional environment variable `--set keycloak-setup.env_vars.KEYCLOAK_RESET_REALM=true`. As this also resets the list of Airbyte users and permissions, please use this with caution.

To deploy Self-Managed Enterprise without SSO, exclude the entire `auth:` section from your values.yml config file. You will authenticate with the instance admin user and password included in your `airbyte.yml`. Without SSO, you cannot currently have unique logins for multiple users.

</details>

### Step 3: Configure your Deployment

1. Inside your `airbyte` directory, create an empty `values.yml` file.

2. Paste the following into your newly created `values.yml` file. This is required to deploy Airbyte Self-Managed Enterprise:

```yml
global:
  edition: enterprise
```

3. The following subsections help you customize your deployment to use an external database, log storage, dedicated ingress, and more. To skip this and deploy a minimal, local version of Self-Managed Enterprise, [jump to Step 4](#step-4-deploy-self-managed-enterprise).

#### Configuring the Airbyte Database

For Self-Managed Enterprise deployments, we recommend using a dedicated database instance for better reliability, and backups (such as AWS RDS or GCP Cloud SQL) instead of the default internal Postgres database (`airbyte/db`) that Airbyte spins up within the Kubernetes cluster.

We assume in the following that you've already configured a Postgres instance:

<details>
<summary>External database setup steps</summary>

1. Add external database details to your `values.yml` file. This disables the default internal Postgres database (`airbyte/db`), and configures the external Postgres database:

```yaml
postgresql:
  enabled: false

externalDatabase:
  host: ## Database host
  user: ## Non-root username for the Airbyte database
  database: db-airbyte ## Database name
  port: 5432 ## Database port number
```

2. For the non-root user's password which has database access, you may use `password`, `existingSecret` or `jdbcUrl`. We recommend using `existingSecret`, or injecting sensitive fields from your own external secret store. Each of these parameters is mutually exclusive:

```yaml
postgresql:
    enabled: false

externalDatabase:
    ...
    password: ## Password for non-root database user
    existingSecret: ## The name of an existing Kubernetes secret containing the password.
    existingSecretPasswordKey: ## The Kubernetes secret key containing the password.
    jdbcUrl: "jdbc:postgresql://<user>:<password>@localhost:5432/db-airbyte" ## Full database JDBC URL. You can also add additional arguments.
```

The optional `jdbcUrl` field should be entered in the following format: `jdbc:postgresql://localhost:5432/db-airbyte`. We recommend against using this unless you need to add additional extra arguments can be passed to the JDBC driver at this time (e.g. to handle SSL).

</details>

#### Configuring External Logging

For Self-Managed Enterprise deployments, we recommend spinning up standalone log storage for additional reliability using tools such as S3 and GCS instead of against using the default internal Minio storage (`airbyte/minio`). It's then a common practice to configure additional log forwarding from external log storage into your observability tool.

<details>
<summary>External log storage setup steps</summary>

Add external log storage details to your `values.yml` file. This disables the default internal Minio instance (`airbyte/minio`), and configures the external log database:

<Tabs>
<TabItem value="S3" label="S3" default>

Ensure you've already created a Kubernetes secret containing both your S3 access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `aws-s3-access-key-id` and `aws-s3-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

```yaml
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

Set `authenticationType` to `instanceProfile` if the compute infrastructure running Airbyte has pre-existing permissions (e.g. IAM role) to read and write from the appropriate buckets.

</TabItem>
<TabItem value="GCS" label="GCS" default>

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `gcp-cred-secrets` Kubernetes secret, under a `gcp.json` file. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

```yaml
global:
  storage:
    type: "GCS"
    storageSecretName: gcp-cred-secrets
    bucket: ## GCS bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    gcs:
      projectId: <project-id>
      credentialsPath: /secrets/gcs-log-creds/gcp.json
```

</TabItem>
</Tabs>
</details>

#### Configuring Ingress

To access the Airbyte UI, you will need to manually attach an ingress configuration to your deployment. The following is a skimmed down definition of an ingress resource you could use for Self-Managed Enterprise:

<details>
<summary>Ingress configuration setup steps</summary>
<Tabs>
<TabItem value="NGINX" label="NGINX">

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: # ingress name, example: enterprise-demo
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
    - host: # host, example: enterprise-demo.airbyte.com
      http:
        paths:
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-webapp-svc
                name: airbyte-enterprise-airbyte-webapp-svc
                port:
                  number: 80 # service port, example: 8080
            path: /
            pathType: Prefix
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
                # format is ${RELEASE_NAME}-airbyte--server-svc
                name: airbyte-enterprise-airbyte-server-svc
                port:
                  number: 8001
            path: /api/public
            pathType: Prefix
```

</TabItem>
<TabItem value="Amazon ALB" label="Amazon ALB">

If you are intending on using Amazon Application Load Balancer (ALB) for ingress, this ingress definition will be close to what's needed to get up and running:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: # ingress name, e.g. enterprise-demo
  annotations:
    # Specifies that the Ingress should use an AWS ALB.
    kubernetes.io/ingress.class: "alb"
    # Redirects HTTP traffic to HTTPS.
    ingress.kubernetes.io/ssl-redirect: "true"
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
    - host: # e.g. enterprise-demo.airbyte.com
      http:
        paths:
          - backend:
              service:
                name: airbyte-enterprise-airbyte-webapp-svc
                port:
                  number: 80
            path: /
            pathType: Prefix
          - backend:
              service:
                name: airbyte-enterprise-airbyte-keycloak-svc
                port:
                  number: 8180
            path: /auth
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-server-svc
                name: airbyte-enterprise-airbyte-server-svc
                port:
                  number: 8001
            path: /api/public
            pathType: Prefix
```

The ALB controller will use a `ServiceAccount` that requires the [following IAM policy](https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json) to be attached.

</TabItem>
</Tabs>
</details>

Once this is complete, ensure that the value of the `webapp-url` field in your `values.yml` is configured to match the ingress URL.

You may configure ingress using a load balancer or an API Gateway. We do not currently support most service meshes (such as Istio). If you are having networking issues after fully deploying Airbyte, please verify that firewalls or lacking permissions are not interfering with pod-pod communication. Please also verify that deployed pods have the right permissions to make requests to your external database.

#### Configuring External Connector Secret Management

Airbyte's default behavior is to store encrypted connector secrets on your cluster as Kubernetes secrets. You may <b>optionally</b> opt to instead store connector secrets in an external secret manager such as AWS Secrets Manager, Google Secrets Manager or Hashicorp Vault. Upon creating a new connector, secrets (e.g. OAuth tokens, database passwords) will be written to, then read from the configured secrets manager.

<details>
<summary>Configuring external connector secret management</summary>

Modifing the configuration of connector secret storage will cause all <i>existing</i> connectors to fail. You will need to recreate these connectors to ensure they are reading from the appropriate secret store.

<Tabs>
<TabItem label="Amazon" value="Amazon">

If authenticating with credentials, ensure you've already created a Kubernetes secret containing both your AWS Secrets Manager access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `aws-secret-manager-access-key-id` and `aws-secret-manager-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

```yaml
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

Set `authenticationType` to `instanceProfile` if the compute infrastructure running Airbyte has pre-existing permissions (e.g. IAM role) to read and write from AWS Secrets Manager.

To decrypt secrets in the secret manager with AWS KMS, configure the `kms` field, and ensure your Kubernetes cluster has pre-existing permissions to read and decrypt secrets.

</TabItem>
<TabItem label="GCP" value="GCP">

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `gcp-cred-secrets` Kubernetes secret, under a `gcp.json` file. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets). For simplicity, we recommend provisioning a single service account with access to both GCS and GSM.

```yaml
secretsManager:
  type: googleSecretManager
  storageSecretName: gcp-cred-secrets
  googleSecretManager:
    projectId: <project-id>
    credentialsSecretKey: gcp.json
```

</TabItem>
</Tabs>

</details>

### Step 4: Deploy Self-Managed Enterprise

Install Airbyte Self-Managed Enterprise on helm using the following command:

```sh
helm install \
--namespace airbyte \
--values ./values.yml \
--set-file airbyteYml="./airbyte.yml" \
airbyte-enterprise \
airbyte/airbyte
```

To uninstall Self-Managed Enterprise, run `helm uninstall airbyte-enterprise`.

## Updating Self-Managed Enterprise

Upgrade Airbyte Self-Managed Enterprise by:

1. Running `helm repo update`. This pulls an up-to-date version of our helm charts, which is tied to a version of the Airbyte platform.
2. Re-installing Airbyte Self-Managed Enterprise:

```sh
helm upgrade \
--namespace airbyte \
--values ./values.yml \
--set-file airbyteYml="./airbyte.yml" \
--install airbyte-enterprise \
airbyte/airbyte
```

## Customizing your Deployment

In order to customize your deployment, you need to create an additional `values.yaml` file in your `airbyte` directory, and populate it with configuration override values. A thorough `values.yaml` example including many configurations can be located in [charts/airbyte](https://github.com/airbytehq/airbyte-platform/blob/main/charts/airbyte/values.yaml) folder of the Airbyte repository.

After specifying your own configuration, run the following command:

```sh
helm upgrade \
--namespace airbyte \
--values path/to/values.yaml
--values ./values.yml \
--set-file airbyteYml="./airbyte.yml" \
--install airbyte-enterprise \
airbyte/airbyte
```

### Customizing your Service Account

You may choose to use your own service account instead of the Airbyte default, `airbyte-sa`. This may allow for better audit trails and resource management specific to your organizational policies and requirements.

To do this, add the following to your `values.yml`:

```
serviceAccount:
  name:
```
