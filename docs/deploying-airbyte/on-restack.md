# On Restack

## Overview
Scaling Airbyte on Kubernetes has never been easier. <br/>[Restack](https://www.restack.io) is a platform that lets you discover and deploy open source tools on Kubernetes. With just a few clicks, you can deploy and scale Airbyte in your own cloud infrastructure on kubernetes so that developers can concentrate on what they do best and don’t have to worry about devops.

## Getting Started

You can start your Airbyte journey with Restack with just a few steps.

  - [Sign up](#sign-up)
  - [Add AWS credentials with AdministratorAccess](#add-aws-credentials-with-administratoraccess)
  - [One-click cluster creation with Restack](#one-click-cluster-creation-with-restack)
  - [Deploy Airbyte on Restack](#deploy-airbyte-on-restack)
  - [Start using Airbyte](#start-using-airbyte)
  - [Deploy multiple instances of Airbyte](#deploy-multiple-instances-of-airbyte)

## Sign up

To Sign-up to Restack, visit [www.restack.io/signup](https://www.restack.io/signup). You can sign up with your corporate email address or your GitHub profile. You do not need a credit card to sign up.
If you already have an account, go ahead and login to Restack at [www.restack.io/login](https://www.restack.io/login)

## Add AWS credentials with AdministratorAccess

Restack’s architecture is designed in such a way, that your products like Airbyte and any data stored is only located in your cloud. The Restack control plane only accesses DevOps related metrics and logs, to maintain Airbyte in your cloud.

To deploy Airbyte in your own AWS infrastructure with Restack, you will need to add your credentials as the next step. 

Please make sure that this account has `AdministratorAccess`. This is how Restack can ensure an end-to-end cluster creation and cluster management process.

1. Navigate to `Clusters` in the left-hand navigation menu.
2. Select the `Credentials` tab.
3. Click on `Add credential`.
4. Give a suitable title to your credentials for managing them later.
5. Enter your `AWS Access Key ID` and `AWS Secret Access key`.
6. Click on `Add credential`.

>[How to get your AWS Access key ID and AWS Secret Access Key](https://docs.aws.amazon.com/accounts/latest/reference/root-user-access-key.html)

## One-click cluster creation with Restack

:::tip
Why do I need a cluster?<br/>
Running your application on a Kubernetes cluster lets you deploy, scale and monitor the application reliably. 
:::
Once you have added your credentials, 
- Navigate to the `Clusters` tab on the same page and click on `Create cluster`.
- Give a suitable name to your cluster.
- Select the region you want to deploy the cluster in.
- Select the AWS credentials you added in the previous step.

The cluster creation process will start automatically. You can sit back and relax. Once the cluster is ready, you will get an email on the email id connected with your account. 
<br/>Creating a cluster is a one-time process. From here you can directly add as many open source tools as you please in this cluster.

Any application you deploy in your cluster will be accessible via a free **restack domain**. 
<br/>Contact the Restack team to set a custom domain per Airbyte instance. 

## Deploy Airbyte on Restack
- Click on `Add application` from the Cluster description or go to the Applications tab in the left hand side navigation.
- Click on `Airbyte`
- Select the cluster you have already provisioned.
- Click on `add application`
- Done!

## Start using Airbyte
Within minutes, Airbyte will be deployed on your cluster and you can access it using the link under the `URL` tab. 
You can also check the workloads and volumes that are deployed within Airbyte.

## Deploy multiple instances of Airbyte
Restack makes it easier to deploy multiple instances of Airbyte on the same or multiple clusters. 
<br/>So you can test the latest version before upgrading or have a dedicated instance for development and for production.