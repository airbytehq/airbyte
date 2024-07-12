
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploying Airbyte

The Airbyte platform is a sophisticated data integration platform that enables you to handle large amounts of data movement.
To quickly deploy Airbyte on your local machine you can visit the [Quickstart](../using-airbyte/getting-started/oss-quickstart) guide.
If setting up an Airbyte server does not fit your usecase needs (i.e. you're using Jupyter Notebooks or iterating on an early prototype for your project) you may find the [PyAirbyte](../using-airbyte/pyairbyte/getting-started) documentation useful. 

:::tip
Enterprise Customers should follow the steps outlined in our docs on [Airbyte Self-Managed Enterprise](../enterprise-setup/README.md) and the associated [implementation guide](../enterprise-setup/implementation-guide.md).
:::

## Understanding the Airbyte Deployment

Airbyte is built to be deployed into a Kubernetes cluster.
You can use a Cloud Provider, such as, AWS, GCP, Azure, or onto a single node, such as an EC2 VM, or even locally on your computer.
We recommend deploying Airbyte using Helm and the documented Helm chart values. 

Helm is a Kubernetes package manager for automating deployment and management of complex applications with microservices on Kubernetes.  Refer to our [Helm Chart Usage Guide](https://airbytehq.github.io/helm-charts/) for more information about how to get started.


[//]: # (The [Infrastructure]&#40;#deploying-airbyte/infrastructure&#41; section describes the Airbyte's recommended cloud infrastructure to set up for each supported platform. Keep in mind that these guides are meant to assist you, but you are not required to follow them. Airbyte is designed to be as flexible as possible in order  to fit into your existing infrastructure.)

## Creating a Namespace for Airbyte

While it is not strictly necessary to isolate the Airbyte installation into its own namespace, it is good practice and recommended as a part of the installation.
This documentation assumes that you chose the name `airbyte` for the namespace, but you may choose a different name if required.

To create a namespace run the following

```sh
kubectl create namespace airbyte
```


## Preconfiguring Kubernetes Secrets

Deploying Airbyte requires specifying a number of sensitive values. These can be API keys, usernames and passwords, etc.
In order to protect these sensitive values, the Helm Chart assumes that these values are pre-configured and stored in a Kubernetes Secret *before* the Helm installation begins. Each [integration](#integrations)  will provide the Secret values that are required for the specific integration.

While you can set the name of the secret to whatever you prefer, you will need to set that name in various places in your values.yaml file. For this reason we suggest that you keep the name of `airbyte-config-secrets` unless you have a reason to change it.

<Tabs>
<TabItem value="yaml" label="Creating Secrets with YAML" default>

You can apply your yaml to the cluster with `kubectl apply -f secrets.yaml -n airbyte` to create the secrets.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  # Examples
  key-1: "value-1"
  key-2: "value-2"
```
</TabItem>

<TabItem value="cli" label="Creating secrets with kubectl">

You can also use `kubectl` to create the secret directly from the CLI:

```sh
kubectl create secret generic airbyte-config-secrets \
  --from-literal=key-1='value-1' \
  --from-literal=key2='value-2' \
  --namespace airbyte
```

</TabItem>
</Tabs>

## Creating a values.yaml override file

To configure your installation of Airbyte, you will need to override specific parts of the Helm Chart. To do this you should create a new file called `values.yaml` somewhere that is accessible during the installation process. 
The documentation has been created to "build up" a values.yaml, so there is no need to copy the whole of the Chart values.yaml, you only need to provide the specific overrides.

Each [Integrations](#integrations) will provide a section of the specific values that you should override and provide examples of what the values should look like. An example `values.yaml` file might look something like:

```yaml
global:
  airbyteUrl: https://airbyte.company.example
  storage:
    type: "S3"
    bucket: ## S3 bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    s3:
      region: "us-east-1"
      authenticationType: "instanceProfile"

    secretsManager:
      type: awsSecretManager
      awsSecretManager:
        region: "us-east-1"
        authenticationType: "instanceProfile"
```


## Integrations

The Airbyte platform is built to integrate with your existing cloud infrastructure. You can 
configure various components of the platform to suit your needs. This includes an object store,
such as S3 or GCS for storing logs and state, a database for externalizing state, and a secret 
manager for keep your secrets secure. Each of these integrations can be configured to suit your 
needs. Their configuration is described in the Integrations section. Each of these integrations has its own section where you'll find an explanation of the rationale for why it's useful to configure the integration. There, you'll also find details about how to configure the integration.

- [State and Logging Storage](./integrations/storage)
- [Secret Management](./integrations/secrets)
- [External Database](./integrations/database)
- [Ingress](./integrations/ingress)


## Installing Airbyte

After you have applied your Secret values to the Cluster and you have filled out a values.yaml file appropriately for your specific configuration,
you can begin a Helm Install. To do this, make sure that you have the [Helm Client](https://helm.sh/docs/intro/install/) installed and on your path.
Then you can run:

```sh
helm install \
airbyte \
airbyte/airbyte
--namespace airbyte \
--values ./values.yaml \
```

After the installation has completed, you can configure your [Ingress](./integrations/ingress) by following the directions for your specific Ingress provider.

<!--
##TODO

## Tools 

### Required Tools

Helm

Kubectl

### Optional Tools

K9s

Stern -->

