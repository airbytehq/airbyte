---
products: oss-community
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Deploy Airbyte to AWS EKS

Airbyte is built to be deployed to a Kubernetes cluster. This tutorial walks you through deploying Airbyte Self-Managed Community, Airbyte's open source product, on [AWS EKS](https://aws.amazon.com/eks/). It is intended for Software/DevOps Engineers who already use, or want to begin using, AWS for infrastructure. It is accessible to beginners, but assumes you have basic knowledge of:

- [Kubernetes](https://kubernetes.io/)
- [Helm](https://helm.sh/)
- [AWS products and infrastructure](https://aws.amazon.com/products/)
- [Kubectl](https://kubernetes.io/docs/reference/kubectl/) and using a command-line interface

By the end of this tutorial, you'll have a production-ready version of Airbyte running on a Kubernetes cluster.

## Background

## Before you start

### Requirements

Before starting this tutorial, have the following components ready to use. It's easiest if they're all running in the [same virtual private cloud](https://docs.aws.amazon.com/eks/latest/userguide/network-reqs.html).

- An [AWS EKS](https://aws.amazon.com/eks/) cluster running on EC2 instances with [2 or more availability zones](https://docs.aws.amazon.com/eks/latest/userguide/disaster-recovery-resiliency.html) and a minimum of 6 nodes
- An [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- A URL to access the Airbyte UI and make API requests <!-- Is that one URL or two? -->
- An [AWS S3](https://aws.amazon.com/s3/) bucket with two directories: one for log storage and another for state storage
- Optional, but recommended: An [Amazon RDS Postgres](https://aws.amazon.com/rds/postgresql/) database
- [Amazon Secrets Manager](https://aws.amazon.com/secrets-manager/) 

### Limitations

## What's involved in an EKS deployment

## What an EKS deployment looks like

## Part 1: Configure Kubernetes Secrets

## Part 2: Add Airbyte Helm Repository

## Part 3: Create a values.yaml file to customize your deployment

## Part 4: Configure a database

## Part 5: Configure external logging

## Part 6: Configure external connector secret management

## Part 7: Configure ingress

## Part 8: Deploy Airbyte

## Part 9: Configure your service account

## Part 10: Upgrading and updating Airbyte
