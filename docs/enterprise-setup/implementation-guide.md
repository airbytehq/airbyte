---
products: oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Implementation Guide

[Airbyte Self-Managed Enterprise](./README.md) is in an early access stage for select priority users. Once you [are qualified for a Self-Managed Enterprise license key](https://airbyte.com/company/talk-to-sales), you can deploy Airbyte with the following instructions.

Airbyte Self-Managed Enterprise must be deployed using Kubernetes. This is to enable Airbyte's best performance and scale. The core components \(api server, scheduler, etc\) run as deployments while the scheduler launches connector-related pods on different nodes.

## Prerequisites

For a production-ready deployment of Self-Managed Enterprise, various infrastructure components are required. We recommend deploying to Amazon EKS or Google Kubernetes Engine. The following diagram illustrates a typical Airbyte deployment running on AWS:

![AWS Architecture Diagram](./assets/self-managed-enterprise-aws.png)

Prior to deploying Self-Managed Enterprise, we recommend having each of the following infrastructure components ready to go. When possible, it's easiest to have all components running in the same [VPC](https://docs.aws.amazon.com/eks/latest/userguide/network_reqs.html). The provided recommendations are for customers deploying to AWS:

| Component                | Recommendation                                                            |
|--------------------------|-----------------------------------------------------------------------------|
| Kubernetes Cluster       | Amazon EKS cluster running in [2 or more availability zones](https://docs.aws.amazon.com/eks/latest/userguide/disaster-recovery-resiliency.html) on a minimum of 6 nodes. |
| Ingress                  | [Amazon ALB](#configuring-ingress) and a URL for users to access the Airbyte UI or make API requests.                                                  |
| Object Storage           | [Amazon S3 bucket](#configuring-external-logging) with two directories for log and state storage.         |
| Dedicated Database       | [Amazon RDS Postgres](#configuring-the-airbyte-database) with at least one read replica.                                               |
| External Secrets Manager | [Amazon Secrets Manager](/operator-guides/configuring-airbyte#secrets) for storing connector secrets.                                               |


We also require you to install and configure the following Kubernetes tooling:
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

## Deploy Airbyte Enterprise

### Add Airbyte Helm Repository

Follow these instructions to add the Airbyte helm repository:
1. Run `helm repo add airbyte https://airbytehq.github.io/helm-charts`, where `airbyte` is the name of the repository that will be indexed locally.
2. Perform the repo indexing process, and ensure your helm repository is up-to-date by running `helm repo update`.
3. You can then browse all charts uploaded to your repository by running `helm search repo airbyte`.

### Clone & Configure Airbyte

1. `git clone` the latest revision of the [airbyte-platform repository](https://github.com/airbytehq/airbyte-platform)

2. Create a new `airbyte.yml` file in the `configs` directory of the `airbyte-platform` folder. You may also copy `airbyte.sample.yml` to use as a template:

```sh
cp configs/airbyte.sample.yml configs/airbyte.yml
```

3. Add your Airbyte Self-Managed Enterprise license key to your `airbyte.yml`. 

4. Add your [auth details](/enterprise-setup/sso) to your `airbyte.yml`. Auth configurations aren't easy to modify after Airbyte is installed, so please double check them to make sure they're accurate before proceeding.

<details>
    <summary>Configuring auth in your airbyte.yml file</summary>

To configure SSO with Okta, add the following at the end of your `airbyte.yml` file:

```yaml
auth:   
    identity-providers:
        -   type: okta
            domain: $OKTA_DOMAIN
            app-name: $OKTA_APP_INTEGRATION_NAME
            client-id: $OKTA_CLIENT_ID
            client-secret: $OKTA_CLIENT_SECRET
```

To configure basic auth (deploy without SSO), remove the entire `auth:` section from your airbyte.yml config file. You will authenticate with the instance admin user and password included in the your `airbyte.yml`.

</details>

#### Configuring the Airbyte Database

For Self-Managed Enterprise deployments, we recommend using a dedicated database instance for better reliability, and backups (such as AWS RDS or GCP Cloud SQL) instead of the default internal Postgres database (`airbyte/db`) that Airbyte spins up within the Kubernetes cluster.

:::info
Currently, Airbyte requires connection to a Postgres 13 instance.
:::

We assume in the following that you've already configured a Postgres instance:

<details>
<summary>External database setup steps</summary>

1. In the `charts/airbyte/values.yaml` file, disable the default Postgres database (`airbyte/db`):

```yaml
postgresql:
    enabled: false
```

2. In the `charts/airbyte/values.yaml` file, enable and configure the external Postgres database:

```yaml
externalDatabase:   
    host: ## Database host
    user: ## Non-root username for the Airbyte database
    database: db-airbyte ## Database name
    port: 5432 ## Database port number 
```

For the non-root user's password which has database access, you may use `password`, `existingSecret` or `jdbcUrl`. We recommend using `existingSecret`, or injecting sensitive fields from your own external secret store. Each of these parameters is mutually exclusive: 

```yaml
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

For Self-Managed Enterprise deployments, we recommend spinning up standalone log storage for additional reliability using tools such as S3 and GCS instead of against using the defaul internal Minio storage (`airbyte/minio`). It's then a common practice to configure additional log forwarding from external log storage into your observability tool.

<details>
<summary>External log storage setup steps</summary>

1. In the `charts/airbyte/values.yaml` file, disable the default Minio instance (`airbyte/minio`):

```yaml
minio:
  enabled: false
```

2. In the `charts/airbyte/values.yaml` file, enable and configure external log storage:


<Tabs>
<TabItem value="S3" label="S3" default>

```yaml
global:
    ...
    log4jConfig: "log4j2-no-minio.xml"

    logs:
        storage:
            type: "S3"
        
        minio:
            enabled: false

        s3:
            enabled: true
            bucket: "" ## S3 bucket name that you've created.
            bucketRegion: "" ## e.g. us-east-1

        accessKey: ## AWS Access Key.
            password: ""
            existingSecret: "" ## The name of an existing Kubernetes secret containing the AWS Access Key.
            existingSecretKey: "" ## The Kubernetes secret key containing the AWS Access Key.

        secretKey: ## AWS Secret Access Key
            password:
            existingSecret: "" ## The name of an existing Kubernetes secret containing the AWS Secret Access Key.
            existingSecretKey: "" ## The name of an existing Kubernetes secret containing the AWS Secret Access Key.
```

For each of `accessKey` and `secretKey`, the `password` and `existingSecret` fields are mutually exclusive.

3. Ensure your access key is tied to an IAM user with the [following policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html#iam-policy-ex0), allowing the user access to S3 storage:

```yaml
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action": "s3:ListAllMyBuckets",
         "Resource":"*"
      },
      {
         "Effect":"Allow",
         "Action":["s3:ListBucket","s3:GetBucketLocation"],
         "Resource":"arn:aws:s3:::YOUR-S3-BUCKET-NAME"
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:GetObject",
            "s3:GetObjectAcl",
            "s3:DeleteObject"
         ],
         "Resource":"arn:aws:s3:::YOUR-S3-BUCKET-NAME/*"
      }
   ]
}
```

</TabItem>
<TabItem value="GKE" label="GKE" default> 


```yaml
global:
    ...
    log4jConfig: "log4j2-no-minio.xml"

    logs:
        storage:
            type: "GCS"
        
        minio:
            enabled: false
            
        gcs:
            bucket: airbyte-dev-logs # GCS bucket name that you've created.
            credentials: ""
            credentialsJson: "" ## Base64 encoded json GCP credentials file contents
```

Note that the `credentials` and `credentialsJson` fields are mutually exclusive.

</TabItem>
</Tabs>
</details>


#### Configuring Ingress

To access the Airbyte UI, you will need to manually attach an ingress configuration to your deployment. The following is a skimmed down definition of an ingress resource you could use for Self-Managed Enterprise:

<details>
<summary>Ingress configuration setup steps</summary>
<Tabs>
<TabItem value="Generic" label="Generic">

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: # ingress name, example: enterprise-demo
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - host: # host, example: enterprise-demo.airbyte.com
    http:
      paths:
      - backend:
          service:
            # format is ${RELEASE_NAME}-airbyte-webapp-svc
            name: airbyte-pro-airbyte-webapp-svc 
            port:
              number: # service port, example: 8080
        path: /
        pathType: Prefix
      - backend:
          service:
            # format is ${RELEASE_NAME}-airbyte-keycloak-svc
            name: airbyte-pro-airbyte-keycloak-svc
            port:
              number: # service port, example: 8180
        path: /auth
        pathType: Prefix
```

</TabItem>
<TabItem value="Amazon ALB" label="Amazon ALB">

If you are intending on using Amazon Application Load Balancer (ALB) for ingress, this ingress definition will be close to what's needed to get up and running:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: <INGRESS_NAME>
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
  - host: <WEBAPP_URL> e.g. enterprise-demo.airbyte.com
    http:
      paths:
      - backend:
          service:
            name: airbyte-pro-airbyte-webapp-svc 
            port:
              number: 80
        path: /
        pathType: Prefix
      - backend:
          service:
            name: airbyte-pro-airbyte-keycloak-svc
            port:
              number: 8180
        path: /auth
        pathType: Prefix
```

The ALB controller will use a `ServiceAccount` that requires the [following IAM policy](https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json) to be attached.

</TabItem>
</Tabs>
</details>

Once this is complete, ensure that the value of the `webapp-url` field in your `airbyte.yml` is configured to match the ingress URL.

You may configure ingress using a load balancer or an API Gateway. We do not currently support most service meshes (such as Istio). If you are having networking issues after fully deploying Airbyte, please verify that firewalls or lacking permissions are not interfering with pod-pod communication. Please also verify that deployed pods have the right permissions to make requests to your external database.

### Install Airbyte Enterprise

Install Airbyte Enterprise on helm using the following command:

```sh
./tools/bin/install_airbyte_pro_on_helm.sh
```

The default release name is `airbyte-pro`. You can change this via the `RELEASE_NAME` environment
variable.

### Customizing your Airbyte Enterprise Deployment

In order to customize your deployment, you need to create `values.yaml` file in a local folder and populate it with default configuration override values. A `values.yaml` example can be located in [charts/airbyte](https://github.com/airbytehq/airbyte-platform/blob/main/charts/airbyte/values.yaml) folder of the Airbyte repository.

After specifying your own configuration, run the following command:

```sh
./tools/bin/install_airbyte_pro_on_helm.sh --values path/to/values.yaml
```
