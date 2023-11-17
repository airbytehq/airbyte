import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Implementation Guide

[Airbyte Self-Managed](./README.md) is in an early access stage for select priority users. Once you [are qualified for an Airbyte Self Managed license key](https://airbyte.com/company/talk-to-sales), you can deploy Airbyte with the following instructions.

Airbyte Self Managed must be deployed using Kubernetes. This is to enable Airbyte's best performance and scale. The core components \(api server, scheduler, etc\) run as deployments while the scheduler launches connector-related pods on different nodes.

## Prerequisites

There are three prerequisites to deploying Self-Managed: installing [helm](https://helm.sh/docs/intro/install/), a Kubernetes cluster, and having configured `kubectl` to connect to the cluster.

For production, we recommend deploying to EKS, GKE or AKS. If you are doing some local testing, follow the cluster setup instructions outlined [here](../../deploying-airbyte/on-kubernetes-via-helm.md#cluster-setup).

To install `kubectl`, please follow [these instructions](https://kubernetes.io/docs/tasks/tools/). To configure `kubectl` to connect to your cluster by using `kubectl use-context my-cluster-name`, see the following:

<details>
    <summary>Configure kubectl to connect to your cluster</summary>
    <Tabs>
        <TabItem value="GKE" label="GKE" default> 
            <ol>
                <li>Configure <code>gcloud</code> with <code>gcloud auth login</code>.</li>
                <li>On the Google Cloud Console, the cluster page will have a "Connect" button, with a command to run locally: <code>gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE_NAME --project $PROJECT_NAME</code></li>
                <li>Use <code>kubectl config get-contexts</code> to show the contexts available.</li>
                <li>Run <code>kubectl config use-context $GKE_CONTEXT</code> to access the cluster from kubectl.</li>
            </ol>
        </TabItem>
        <TabItem value="EKS" label="EKS">
            <ol>
                <li><a href="https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html">Configure your AWS CLI</a> to connect to your project.</li>
                <li>Install <a href="https://eksctl.io/introduction/">eksctl</a>.</li>
                <li>Run <code>eksctl utils write-kubeconfig --cluster=$CLUSTER_NAME</code> to make the context available to kubectl.</li>
                <li>Use <code>kubectl config get-contexts</code> to show the contexts available.</li>
                <li>Run <code>kubectl config use-context $EKS_CONTEXT</code> to access the cluster with kubectl.</li>
            </ol>
        </TabItem>
    </Tabs>
</details>

## Deploy Airbyte Self-Managed

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

3. Add your Airbyte Enterprise license key to your `airbyte.yml`. 

4. Add your [auth details](/airbyte-enterprise#single-sign-on-sso) to your `airbyte.yml`. Auth configurations aren't easy to modify after Airbyte is installed, so please double check them to make sure they're accurate before proceeding.

<details>
    <summary>Configuring auth in your airbyte.yml file</summary>

To configure SSO with Okta, add the following at the end of your `airbyte.yml` file:

```
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

### Install Airbyte Self Managed

Install Airbyte Enterprise on helm using the following command:

```text
./tools/bin/install_airbyte_pro_on_helm.sh
```

The default release name is `airbyte-pro`. You can change this via the `RELEASE_NAME` environment
variable.

### Customizing your Airbyte Self Managed Deployment

In order to customize your deployment, you need to create `values.yaml` file in a local folder and populate it with default configuration override values. A `values.yaml` example can be located in [charts/airbyte](https://github.com/airbytehq/airbyte-platform/blob/main/charts/airbyte/values.yaml) folder of the Airbyte repository.

After specifying your own configuration, run the following command:

```text
./tools/bin/install_airbyte_pro_on_helm.sh --values path/to/values.yaml $RELEASE_NAME airbyte/airbyte
```