
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploying Airbyte

The Airbyte platform is a sophisticated data integration platform that enables you to handle large amounts of data movement. If setting up an Airbyte server does not fit your usecase needs (i.e. you're using Jupyter Notebooks or iterating on an early prototype for your project) you may find the [PyAirbyte](./using-airbyte/pyairbyte/getting-started) documentation useful. To quickly deploy Airbyte on your local machine you can visit the 
[Quickstart](./using-airbyte/getting-started/oss-quickstart) guide.

:::tip
Enterprise Customers should refer to our docs on [Airbyte Self-Managed Enterprise](../enterprise-setup/README.md) and the associated [implementation guide](../enterprise-setup/implementation-guide.md).
:::

## Understanding the Airbyte Deployment

Airbyte is built to be deployed on top of Kubernetes in a cloud environment. We recommend deploying Airbyte using Helm and the documented Helm chart values. 

Helm is a Kubernetes package manager for automating deployment and management of complex applications with microservices on Kubernetes.  Refer to our [Helm Chart Usage Guide](https://airbytehq.github.io/helm-charts/) for more information about how to get started.


The [Infrastructure](#deploying-airbyte/infrastructure) section describes the Airbyte's recommended cloud infrastructure to set up for each supported platform. Keep in mind that these guides are meant to assist you, but you are not required to follow them. Airbyte is designed to be as flexible as possible in order  to fit into your existing infrastructure.

## Integrations

The Airbyte platform is built to integrate with your existing cloud infrastructure. You can 
configure various components of the platform to suit your needs. This includes an object store,
such as S3 or GCS for storing logs and state, a database for externalizing state, and a secret 
manager for keep your secrets secure. Each of these integrations can be configured to suit your 
needs. Their configuration is described in the [Integrations](#deploying-airbyte/integrations) 
section. Each of these integrations has its own section where you'll find an explanation of the rationale for why it's useful to configure the integration. There, you'll also find details about how to configure the integration.

<details>
<summary> Integration Section Links </summary>

- [State and Logging Storage](./deploying-airbyte/integrations/storage)
- [Secret Management](./deploying-airbyte/integrations/secrets)
- [External Database](./deploying-airbyte/integrations/database)
- [Monitoring](./deploying-airbyte/integrations/monitoring)
- [Ingress](./deploying-airbyte/integrations/ingress)

</details>

<!--
##TODO

## Tools 

### Required Tools

Helm

Kubectl

### Optional Tools

K9s

Stern -->


## Preconfiguring Kubernetes Secrets

We use a secret to pull values out of it should look like this:

While you can set the name of the secret to whatever you prefer, you will need to set that name in various places in your values.yaml file. For this reason we suggest that you keep the name of `airbyte-config-secrets` unless you have a reason to change it.

<Tabs>
<TabItem value="S3" label="S3" default>

**Option 1: create a `values.yaml` file**

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
  database-host: ## e.g. database.internla
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

  # AWS Secret Manager
  aws-secret-manager-access-key-id: ## e.g. AKIAIOSFODNN7EXAMPLE
  aws-secret-manager-secret-access-key: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

```

**Option 2: Create the secret in the CLI**

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

