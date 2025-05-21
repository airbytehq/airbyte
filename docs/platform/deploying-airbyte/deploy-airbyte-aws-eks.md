---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploy Airbyte to AWS EKS

Airbyte runs on a Kubernetes cluster. This tutorial walks you through deploying Airbyte on [AWS EKS](https://aws.amazon.com/eks/). This guide is for Software/DevOps Engineers who want to run Airbyte on AWS infrastructure. It's accessible to beginners, but assumes you have functional knowledge of:

- [Kubernetes](https://kubernetes.io/)
- [Helm](https://helm.sh/)
- [AWS products and infrastructure](https://aws.amazon.com/products/)
- [Kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [AWS CLI](https://aws.amazon.com/cli/)
- [eksctl](https://eksctl.io/)

Data Engineers without this experience may struggle to complete all of these steps, so ask your infrastructure team for help if you need it.

By the end of this tutorial, you'll have a production-ready version of Airbyte running on an EKS cluster.

<!-- :::note
If you aren't a Kubernetes expert or don't actually need to run on EKS, [deploying to EC2](deploy-airbyte-aws-ec2) is usually simpler.
::: -->

## Before you start

### Requirements

Before starting this tutorial, install the following tools on your local machine and add them to your PATH.

- [Helm](https://helm.sh/docs/intro/install/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [AWS CLI](https://aws.amazon.com/cli/)
- [eksctl](https://eksctl.io/installation/#docker)

### Limitations

Things to keep in mind.

- It's easiest if all your customizations run in the [same virtual private cloud](https://docs.aws.amazon.com/eks/latest/userguide/network-reqs.html).

## What involved in an EKS deployment

At a high level, this is what you're building:

- An [AWS EKS](https://aws.amazon.com/eks/) cluster running on EC2 instances with [2 or more availability zones](https://docs.aws.amazon.com/eks/latest/userguide/disaster-recovery-resiliency.html) and a minimum of 6 nodes. Each instance should have at least 2 cores and 8-GB of RAM.
- An [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html) and a URL to access the Airbyte UI and make API requests.
- An [S3](https://aws.amazon.com/s3/) bucket with two directories: one for log storage and another for state storage.
- An [Amazon RDS Postgres](https://aws.amazon.com/rds/postgresql/) database.
- [Amazon Secrets Manager](https://aws.amazon.com/secrets-manager/) to store connector secrets.

Technically, Airbyte only requires the EKS cluster to run. However, your production deployment would suffer from serious limitations if you omit the rest of this infrastructure. It's important you add these into your plan.

![AWS EKS](aws-eks.png)

## Part 1: Set up your infrastructure

In almost all cases, Airbyte's defaults have limitations that make them insufficient for a production deployment on EKS.



## Part 2: Configure Kubernetes secrets

## Part 2: Authenticate and connect to AWS

Before you can deploy Airbyte, authenticate with AWS and connect to your EKS cluster.

1. Authenticate with AWS. The wizard is easiest, but there are [other options](https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html).

    ```bash
    aws configure
    ```

    You must supply your AWS Access Key ID and AWS Secret Access Key. You can also supply a default region name and default output format, if you have a preference.

2. Connect `kubctl` to your EKS cluster. [Learn more about connecting to EKS](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html).

    1. Create or update a `kubeconfig` file for your cluster. Replace `us-west-1` with the AWS Region that your cluster is in and replace `airbyte` with the name of your cluster, if yours are different.

        ```bash
        aws eks update-kubeconfig --region us-west-1 --name airbyte
        ```

        You should see something like this:

        ```bash
        Added new context arn:aws:eks:us-west-1:432613289033:cluster/airbyte to /Users/art.vandelay/.kube/config
        ```

    2. Test your configuration.

        ```bash
        kubectl get svc
        ```
        
        You should see something like this:

        ```bash
        NAME             TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
        svc/kubernetes   ClusterIP   10.100.0.1   <none>        443/TCP   1m
        ```

        If you see errors, troubleshoot with [Unauthorized or access denied (kubectl)](https://docs.aws.amazon.com/eks/latest/userguide/troubleshooting.html#unauthorized).

## Part 3: Add the Airbyte Helm repository

The Airbyte deployment process uses a Helm chart, which is a package for Kubernetes applications. It's like a blueprint or template that defines the resources needed to deploy an application on a Kubernetes cluster. Charts are stored in `helm-repo`.

1. Add the Helm charts. In this example, `airbyte` represents the name of the repository you'll index locally.

    ```bash
    helm repo add airbyte https://airbytehq.github.io/helm-charts
    ```

2. Index the repo.

    ```bash
    helm repo update
    ```

3. If you want to browse all the Helm charts added to your local repo, run:

    ```bash
    helm search repo airbyte
    ```

    The output should look something like this:

    ```bash
    NAME                               	CHART VERSION	APP VERSION	DESCRIPTION                                       
    airbyte/airbyte                    	1.3.0        	1.3.0      	Helm chart to deploy airbyte                      
    airbyte/airbyte-api-server         	0.293.4      	0.63.8     	Helm chart to deploy airbyte-api-server           
    airbyte/airbyte-bootloader         	1.3.0        	1.3.0      	Helm chart to deploy airbyte-bootloader           
    airbyte/airbyte-cron               	0.40.37      	0.40.17    	Helm chart to deploy airbyte-cron                 
    airbyte/airbyte-workload-api-server	0.49.18      	0.50.33    	Helm chart to deploy airbyte-api-server           
    airbyte/connector-builder-server   	1.3.0        	1.3.0      	Helm chart to deploy airbyte-connector-builder-...
    airbyte/connector-rollout-worker   	1.3.0        	1.3.0      	Helm chart to deploy airbyte-connector-rollout-...
    airbyte/cron                       	1.3.0        	1.3.0      	Helm chart to deploy airbyte-cron                 
    airbyte/keycloak                   	1.3.0        	1.3.0      	Helm chart to deploy airbyte-keycloak             
    airbyte/keycloak-setup             	1.3.0        	1.3.0      	Helm chart to deploy airbyte-keycloak-setup       
    airbyte/metrics                    	1.3.0        	1.3.0      	Helm chart to deploy airbyte-metrics              
    airbyte/pod-sweeper                	1.3.0        	1.3.0      	Helm chart to deploy airbyte-pod-sweeper          
    airbyte/server                     	1.3.0        	1.3.0      	Helm chart to deploy airbyte-server               
    airbyte/temporal                   	1.3.0        	1.3.0      	Helm chart to deploy airbyte-temporal             
    airbyte/temporal-ui                	1.3.0        	1.3.0      	Helm chart to deploy airbyte-temporal-ui          
    airbyte/webapp                     	1.3.0        	1.3.0      	Helm chart to deploy airbyte-webapp               
    airbyte/worker                     	1.3.0        	1.3.0      	Helm chart to deploy airbyte-worker               
    airbyte/workload-api               	0.50.3       	0.50.35    	Helm chart to deploy the workload-api service     
    airbyte/workload-api-server        	1.3.0        	1.3.0      	Helm chart to deploy the workload-api service     
    airbyte/workload-launcher          	1.3.0        	1.3.0      	Helm chart to deploy airbyte-workload-launcher 
    ```

## Part 4: Create a namespace for Airbyte

It's not strictly necessary to isolate the Airbyte installation into its own namespace, but this is a best practice. This example assumes you choose the name `airbyte` for the namespace, but you can choose a different name.

To create a namespace run the following command.

```bash
kubectl create namespace airbyte
```

You should see something like this:

```bash
namespace/airbyte created
```

## Part 5: Configure your customizations

Airbyte has everything you need to use the product. In some cases, Airbyte's defaults are enough, but they do have limitations and aren't for everyone.

<!-- Bryce has a good example here of a "complete" secrets and values file: https://github.com/airbytehq/airbyte/discussions/47256#discussioncomment-11082158 -->

### Create a values.yaml file to customize your deployment

### Configure a database

### Configure external logging

### Configure audit logging (Self-Managed Enterprise only)

### Configure external connector secret management

### Configure ingress

### Configure authentication

### Configure a custom image registry

### Configure your service account

## Part 6: Deploy Airbyte {#deploy-airbyte}

Once you have applied your secret values to your Kubernetes cluster and completed your `values.yaml` file with your customizations, you're ready to deploy Airbyte.

  1. Install Airbyte.

      ```bash
      helm install \
      airbyte \
      airbyte/airbyte \
      --namespace airbyte \
      --values ./values.yaml
      ```

      If you are not using any customizations or secrets (rare), use this command, instead:

      ```bash
      helm install \
      airbyte \
      airbyte/airbyte \
      --namespace airbyte  
      ```

  2. Set up port forwarding so you can access your Airbyte UI.

      ```bash
      export POD_NAME=$(kubectl get pods --namespace airbyte -l "app.kubernetes.io/name=webapp" -o jsonpath="{.items[0].metadata.name}")
      export CONTAINER_PORT=$(kubectl get pod --namespace airbyte $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
      echo "Visit http://127.0.0.1:8080 to use your application"
      kubectl --namespace airbyte port-forward $POD_NAME 8080:$CONTAINER_PORT
      ```

You can now access Airbyte in your browser at: http://127.0.0.1:8080 or, if you set up a URL earlier, you can use that URL.

## What's next

You now have a fully functional production deployment of Airbyte.

- **Move data**: In Airbyte, you move data from [sources](../using-airbyte/getting-started/add-a-source) to [destinations](../using-airbyte/getting-started/add-a-destination.md). The relationship between a source and a destination is called a [connection](../using-airbyte/getting-started/set-up-a-connection.md). Try moving some data.
- **Change customizations**: If something about your cloud infrastructure changes later on, make the corresponding update in your `values.yaml` file, then rerun [`helm install`](#deploy-airbyte).
- **Update Airbyte**: Airbyte releases new versions of the Airbyte platform and its connectors regularly. [Keep Airbyte up to date](../operator-guides/upgrading-airbyte.md) to get the latest features and fixes.
