---
products: oss-community, oss-enterprise
---

# Deploy Airbyte

All self-managed instances of Airbyte must be deployed somewhere that can handle large volumes of data movement. When you deploy Airbyte, you create a production-ready environment to move your data.

## Overview

Airbyte must be deployed to a Kubernetes cluster. However, there is great flexibility in how you achieve this. You can deploy to a cloud provider like AWS EKS, Google Cloud, or Azure. You can also deploy to a single node like an AWS EC2, Google GCE, or an Azure Virtual Machine. Some options are easier than others and are more suitable to those with less Kubernetes experience.

## Before you start

### Make sure self-managing is for you

There are many reasons you might want to self-manage Airbyte, but not everyone needs to. If you don't, sign up for an [Airbyte Cloud](https://cloud.airbyte.com/signup) trial and [start syncing data](../using-airbye/getting-started/add-a-source) now. Airbyte Cloud has lower administrative overhead and, depending on your situation, [can be less expensive](https://build-vs-buy.airbyte.com/) than the cloud infrastructure needed to support a robust open source deployment.

If you want to use Python to move data, our Python library, [PyAirbyte](../pyairbyte/getting-started), might be the best fit for you. It's a good choice if you're using Jupyter Notebook or iterating on an early prototype for a large data project and don't need to run a server.

### Try the quickstart

If you haven't already, you might like to try deploying Airbyte locally using our [Quickstart](../using-airbyte/getting-started/oss-quickstart) to get a feel for how it works. However, this is optional.

### Suggested resources {#suggested-resources}

For best performance, run Airbyte on a machine with 4 or more CPUs and at least 8GB of memory. We also support running Airbyte with 2 CPUs and 8GM of memory in low-resource mode. Follow this [Github discussion](https://github.com/airbytehq/airbyte/discussions/44391) to upvote and track progress toward supporting lower resource environments.

### Integrations with other services

Airbyte has everything you need to use the product. In some cases, Airbyte's defaults are enough, but they do have limitations and aren't for everyone. Consider these integrations as part of your Airbyte deployment. You should take some time now to think about these things before you begin:

- **State and logging storage**: Airbyte relies on this data for incremental syncs, and logs help you diagnose issues like failed syncs. Airbyte uses MinIO S3-compatible data storage by default, but if you're deploying to a cloud provider, you may wish to use that provider's simple storage solution.
- **External databases**: Airbyte creates a default Postgres database. For better reliability and regular backups, you may wish to use a dedicated database instance that is backed up on a schedule.
- **Managing secrets**: In the course of using Airbyte, you'll provide it with a number of sensitive values, like API keys, user names, and passwords. By default, Airbyte stores these values in plain text in your configured database. You should take steps to protect these values with an external secret manager.
- **Ingress**: How people access your Airbyte UI and API. Depending on where you deploy Airbyte, default ingress differs. You might need a load balancer, subdomain (airbyte.example.com), and an ingress controller.
- **Authentication**: How people authenticate to access Airbyte. Self-Managed Community supports a single user with a user name and password, but our Enterprise plan offers more options.
- **Custom image repositories**: Where your Docker images live. Airbyte defaults to Docker Hub as its image registry, but you can also use public and private registries in your custom image registry service.

## Start your deployment

Choose the deployment guide that's right for you.

- [AWS EKS](deploy-airbyte-aws-eks)
- [AWS EC2](deploy-airbyte-aws-ec2)
- [Google Cloud GKE](https://www.example.com)
- [Google Cloud GCE](https://www.example.com)

:::note
- [AWS Fargate](https://aws.amazon.com/fargate/) is not currently supported.
- [AWS ECS](https://aws.amazon.com/ecs/) is not currently supported.
:::
