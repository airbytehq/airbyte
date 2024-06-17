
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploying Airbyte

The Airbyte platform is a sophisticated data integration platform that is built to handle large 
amounts of data movement. If you are looking for a more streamlined way to run Airbyte connectors
you can visit the [PyAibyte](#using-airbyte/pyairbyte/getting-started) documentation. If you are 
looking to quickly deploy Airbyte on your local machine you can visit the 
[Quickstart](#deploying-airbyte/quickstart) guide.

## Understanding the Airbyte Deployment

Airbyte is a platform that is built to be deployed in a cloud environment. The platform has been 
built on top of Kubernetes. The recommended way of deploying Airbyte is to use Helm and the 
documented Helm chart values. The Helm chart is available in the Airbyte repository here: #TODO

The [Ingrastructure](#deploying-airbyte/infrastructure) section describes the Airbyte's recommended
way to setup the needed Cloud Infrastructure for each supported platform. These guides will help you
setup the necessary infrastructure for deploying Airbyte, but you are not required to follow these
guides and Airbyte tries to be as flexible as possible to fit into your existing infrastructure.

## Integrations

The Airbyte platform has been built to integrate into your Cloud infrastructure. You can 
configure various components of the platform to suit your needs. This includes an object store,
such as S3 or GCS for storing logs and state, a database for externalizing state, and a secret 
manager for keep your secrets secure. Each of these integrations can be configured to suit your 
needs. Their configuration is described in the [Integrations](#deploying-airbyte/integrations) 
section. Each of these integrations has a longer description of why you would want to configure
the integration, as well as, how to configure the integration.

## Preconfiguring Kubernetes Secrets

We use a secret to pull values out of it should look like this:

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
  database-host: ## e.g. database.internla
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


## Tools 

### Required Tools

Helm

Kubectl

### Optional Tools

K9s

Stern

