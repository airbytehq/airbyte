---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploying Airbyte

The Airbyte platform is a sophisticated data integration platform that enables you to handle large amounts of data movement.
To quickly deploy Airbyte on your local machine you can visit the [Quickstart](../using-airbyte/getting-started/oss-quickstart) guide.
If setting up an Airbyte server does not fit your use case needs (i.e. you're using Jupyter Notebooks or iterating on an early prototype for your project) you may find the [PyAirbyte](../using-airbyte/pyairbyte/getting-started) documentation useful. 

:::tip
Enterprise Customers should follow the steps outlined in our docs on [Airbyte Self-Managed Enterprise](../enterprise-setup/README.md) and the associated [implementation guide](../enterprise-setup/implementation-guide.md).
:::

## Understanding the Airbyte Deployment

Airbyte is built to be deployed into a Kubernetes cluster.
You can use a Cloud Provider, such as, AWS, GCP, Azure, or onto a single node, such as an EC2 VM, or even locally on your computer.

We highly recommend deploying Airbyte using Helm and the documented Helm chart values. 

Helm is a Kubernetes package manager for automating deployment and management of complex applications with microservices on Kubernetes.  Refer to our [Helm Chart Usage Guide](https://airbytehq.github.io/helm-charts/) for more information about how to get started.


The [Infrastructure](infrastructure/aws) section describes the Airbyte's recommended cloud infrastructure to set up for each supported platform. Keep in mind that these guides are meant to assist you, but you are not required to follow them. Airbyte is designed to be as flexible as possible in order to fit into your existing infrastructure.

## Adding the Helm Repository

The deployment will use a Helm chart which is a package for Kubernetes applications, acting like a blueprint or template that defines the resources needed to deploy an application on a Kubernetes cluster. Charts are stored in `helm-repo`.

To add a remote helm repo:
1. Run: `helm repo add airbyte https://airbytehq.github.io/helm-charts`. In this example, `airbyte` is being used to represent the name of the repository that will be indexed locally.

2. After adding the repo, perform the repo indexing process by running `helm repo update`.

3. You can now browse all charts uploaded to repository by running `helm search repo airbyte`

An example of the chart output: 

```text
NAME                               	CHART VERSION	APP VERSION	DESCRIPTION                                       
airbyte/airbyte                    	0.290.0      	0.63.6     	Helm chart to deploy airbyte                      
airbyte/airbyte-api-server         	0.290.0      	0.63.6     	Helm chart to deploy airbyte-api-server           
airbyte/airbyte-bootloader         	0.290.0      	0.63.6     	Helm chart to deploy airbyte-bootloader           
airbyte/airbyte-cron               	0.40.37      	0.40.17    	Helm chart to deploy airbyte-cron                 
airbyte/airbyte-workload-api-server	0.49.18      	0.50.33    	Helm chart to deploy airbyte-api-server           
airbyte/connector-builder-server   	0.290.0      	0.63.6     	Helm chart to deploy airbyte-connector-builder-...
airbyte/cron                       	0.290.0      	0.63.6     	Helm chart to deploy airbyte-cron                 
airbyte/keycloak                   	0.290.0      	0.63.6     	Helm chart to deploy airbyte-keycloak             
airbyte/keycloak-setup             	0.290.0      	0.63.6     	Helm chart to deploy airbyte-keycloak-setup       
airbyte/metrics                    	0.290.0      	0.63.6     	Helm chart to deploy airbyte-metrics              
airbyte/pod-sweeper                	0.290.0      	0.63.6     	Helm chart to deploy airbyte-pod-sweeper          
airbyte/server                     	0.290.0      	0.63.6     	Helm chart to deploy airbyte-server               
airbyte/temporal                   	0.290.0      	0.63.6     	Helm chart to deploy airbyte-temporal             
airbyte/webapp                     	0.290.0      	0.63.6     	Helm chart to deploy airbyte-webapp               
airbyte/worker                     	0.290.0      	0.63.6     	Helm chart to deploy airbyte-worker               
airbyte/workload-api               	0.50.3       	0.50.35    	Helm chart to deploy the workload-api service     
airbyte/workload-api-server        	0.290.0      	0.63.6     	Helm chart to deploy the workload-api service     
airbyte/workload-launcher          	0.290.0      	0.63.6     	Helm chart to deploy airbyte-workload-launcher    
```


## Creating a Namespace for Airbyte

While it is not strictly necessary to isolate the Airbyte installation into its own namespace, it is good practice and recommended as a part of the installation.
This documentation assumes that you chose the name `airbyte` for the namespace, but you may choose a different name if required.

To create a namespace run the following:

```sh
kubectl create namespace airbyte
```


## Preconfiguring Kubernetes Secrets

Deploying Airbyte requires specifying a number of sensitive values. These can be API keys, usernames and passwords, etc.
In order to protect these sensitive values, the Helm Chart assumes that these values are pre-configured and stored in a Kubernetes Secret *before* the Helm installation begins. Each [integration](#integrations) will provide the Secret values that are required for the specific integration.

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
The documentation has been created to "build up" a values.yaml, so there is no need to copy the whole of the Chart values.yaml. You only need to provide the specific overrides.

Each [Integration](#integrations) will provide a section of the specific values that you should override and provide examples of what the values should look like. An example `values.yaml` file may look like the following: 

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

The Airbyte platform is built to integrate with your existing cloud infrastructure. You can configure various components of the platform to suit your needs. This includes an object store, such as S3 or GCS for storing logs and state, a database for externalizing state, and a secrets manager for keep your secrets secure. 

Each of these integrations can be configured to suit your specific needs and is described in the [Integration](#integrations) section. Each of these integrations has its own section where you'll find an explanation for why it's useful to configure the integration. There, you'll also find details about how to configure the integration.

- [State and Logging Storage](./integrations/storage)
- [Secret Management](./integrations/secrets)
- [External Database](./integrations/database)
- [Ingress](./integrations/ingress)


## Installing Airbyte

After you have applied your Secret values to the Cluster and you have filled out a values.yaml file appropriately for your specific configuration, you can begin a Helm Install. To do this, make sure that you have the [Helm Client](https://helm.sh/docs/intro/install/) installed and on your path.
Then you can run:

```sh
helm install \
airbyte \
airbyte/airbyte
--namespace airbyte \
--values ./values.yaml \
```

After the installation has completed, you can configure your [Ingress](./integrations/ingress) by following the directions for your specific Ingress provider.

:::note
As part of maintainging your Airbyte instance, you'll need to do periodic upgrades. See our documentation on [when and how to upgrade Airbyte](../operator-guides/upgrading-airbyte.md) for details. 
:::

<!--
##TODO

## Tools 

### Required Tools

Helm

Kubectl

### Optional Tools

K9s

Stern -->

