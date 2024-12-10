---
products: oss-community
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploy Airbyte

All self-managed instances of Airbyte must be deployed somewhere that can handle large volumes of data movement. Airbyte is built to be deployed to a Kubernetes cluster. You can deploy to a cloud provider like AWS EKS, Google Cloud, or Azure. You can also deploy to a single node like an AWS EC2 virtual machine.

## Overview

Our deployment guides show you how to deploy Airbyte to a production-ready Kubernetes cluster using [Helm](https://helm.sh/). Helm is a Kubernetes package manager for automating deployment and management of complex applications with microservices on Kubernetes.

If you do not want to self-manage Airbyte, skip this guide. Sign up for an [Airbyte Cloud](https://cloud.airbyte.com/signup) trial and [start syncing data](../using-airbye/getting-started/add-a-source) now.

If you want to use Python to move data, our Python library, [PyAirbyte](../pyairbyte/getting-started), might be the best fit for you. It's a good choice if you're using Jupyter Notebook or iterating on an early prototype for a large data project and don't need to run a server.

## Before you start

If you haven't already, you might like to try deploying Airbyte locally using our [Quickstart](../using-airbyte/getting-started/oss-quickstart) to get a feel for how it works. However, this is optional.

## Things to think about as part of a deployment

You likely want to consider a number of customizations as part of your Airbyte deployment. Our guides walk you through these options, but you should take some time to think about these things before you begin:

- **State and logging storage**: Where to store sync state data and logs. Airbyte relies on this data for incremental syncs, and logs help you diagnose issues like failed syncs.
- **Managing secrets**: Airbyte requires a number of sensitive values, like API keys, user names, and passwords. You must take steps to protect these values.
- **External databases**: Airbyte creates a default Postgres database, but for better reliability and backups, you should use a dedicated database instance.
- **Ingress**: How people will access your Airbyte UI and API.
- **Authentication**: How people will authenticate to access Airbyte.

## Start your deployment

Choose the deployment guide that's right for your infrastructure.

- [AWS EKS multi-node](deploying-airbyte-aws-eks)
- [AWS EC2 single node](https://www.example.com)
- [Google Cloud](https://www.example.com)
- [Azure](https://www.example.com)
- [OpenShift](https://www.example.com)
