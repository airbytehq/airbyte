---
products: cloud
---

# PrivateLink

<!-- Confirm which subscriptions include PrivateLink -->

PrivateLink is a cloud networking feature that lets you access a service privately over the cloud provider's internal network—without using the public internet and without exposing public IPs. PrivateLink allows Airbyte Cloud to securely connect to your data sources and destinations without exposing them to the public internet. Traffic between Airbyte and your resources stays entirely within your cloud provider's private network, providing enhanced security for organizations with strict network isolation requirements.

## Why use PrivateLink

Most organizatons don't need to use PrivateLink. However, some organizatons want to benefit from the simplicity and efficiency of SaaS software while maintaining a heightened security posture and more comprehensive data protection needs. PrivateLink offers several advantages for security-conscious organizations.

- **No public IP exposure**: Your data sources and destinations remain completely private. There's no need to assign public IP addresses or open firewall rules to the internet.

- **Traffic stays on the cloud provider's network**: All data transferred between Airbyte and your resources travels through the cloud provider's private backbone, never traversing the public internet.

- **Simplified network security**: Instead of managing complex firewall rules and IP allowlists, you control access through the cloud provider's native endpoint service permissions.

- **Reduced attack surface**: By eliminating public endpoints, you reduce the potential vectors for unauthorized access to your data infrastructure.

## How it works

With PrivateLink, you create a VPC endpoint service in your cloud account that exposes your data source or destination. Airbyte then creates a VPC endpoint that connects to your endpoint service, establishing a private network path between Airbyte's infrastructure and your resources.

When a sync runs, Airbyte routes traffic through this private connection rather than over the public internet. Your resources never need public IP addresses or internet-facing firewall rules—all communication happens within the cloud provider's internal network.

Airbyte maintains dedicated infrastructure for PrivateLink connections, ensuring that only your workspace's sync jobs can access your endpoint.

### Security model

Airbyte's PrivateLink implementation ensures that only sync jobs from your workspace can access your PrivateLink endpoint. Each workspace is assigned a unique security token, and Airbyte's infrastructure enforces network-level isolation so that jobs from other workspaces cannot reach your endpoint—even if they run on shared infrastructure.

### Limitations and considerations

PrivateLink is currently available for AWS only. Support for other cloud providers may be added in the future.

PrivateLink connections are limited to sources and destinations running in AWS. This includes services like Snowflake, Databricks, and PostgreSQL hosted on AWS. If you need to connect to resources outside of AWS, PrivateLink is not currently an option.

For managed AWS services like RDS or Aurora, additional configuration is required to expose them via PrivateLink. See [Using PrivateLink with Managed Services](#using-privatelink-with-managed-services) for details.

### Supported regions

<!-- Contact Airbyte to confirm which regions are currently supported for PrivateLink connections. -->

## Prerequisites

Before setting up PrivateLink, ensure you have the following:

- **Airbyte Cloud account**: An active Airbyte Cloud subscription is required.

- **AWS infrastructure**: Your source or destination must be running in AWS, since PrivateLink is currently AWS-only.

- **Permissions to create VPC endpoint services**: You need IAM permissions to create and configure VPC endpoint services in your AWS account, including:
  - `ec2:CreateVpcEndpointServiceConfiguration`
  - `ec2:ModifyVpcEndpointServicePermissions`
  - `ec2:DescribeVpcEndpointServiceConfigurations`

- **Network Load Balancer (NLB)**: AWS PrivateLink requires a Network Load Balancer in front of your target service. If your service doesn't already have one, you'll need to create it as part of the setup process. This requires additional IAM permissions:
  - `elasticloadbalancing:CreateLoadBalancer`
  - `elasticloadbalancing:CreateTargetGroup`
  - `elasticloadbalancing:RegisterTargets`

## Set up PrivateLink

### Step 1: Contact Airbyte

Before configuring any infrastructure, contact Airbyte to discuss your PrivateLink requirements. Airbyte will confirm region availability and provide you with the AWS account ID you'll need to grant access to your endpoint service.

### Step 2: Create a VPC Endpoint Service

Create a VPC endpoint service in your AWS account that exposes your data source or destination:

1. If your service doesn't already have a Network Load Balancer, create one that targets your service. See [Create a Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-network-load-balancer.html) in the AWS documentation.

2. Create a VPC endpoint service configuration that points to your Network Load Balancer. See [Create an endpoint service](https://docs.aws.amazon.com/vpc/latest/privatelink/create-endpoint-service.html) in the AWS documentation.

3. Note your endpoint service name—it follows the format `com.amazonaws.vpce.{region}.vpce-svc-{id}`. You'll provide this to Airbyte in Step 4.

### Step 3: Configure permissions for Airbyte

Add Airbyte's AWS account as an allowed principal on your endpoint service. This allows Airbyte to create a VPC endpoint that connects to your service.

See [Manage permissions](https://docs.aws.amazon.com/vpc/latest/privatelink/configure-endpoint-service.html#add-remove-permissions) in the AWS documentation for instructions on adding principals to your endpoint service.

### Step 4: Provide your endpoint service name to Airbyte

Share your endpoint service name with Airbyte. Airbyte will create a VPC endpoint on their side and complete the connection setup. Once configured, your PrivateLink connection will be ready to use with your Airbyte connections.

## Using PrivateLink with Managed Services

Managed AWS services like Amazon RDS and Aurora don't natively support VPC endpoint services. To use PrivateLink with these services, you need to set up additional infrastructure to expose them via a Network Load Balancer.

AWS provides a guide for this configuration: [Access Amazon RDS across VPCs using AWS PrivateLink and Network Load Balancer](https://aws.amazon.com/blogs/database/access-amazon-rds-across-vpcs-using-aws-privatelink-and-network-load-balancer/).

The general approach involves creating an NLB that targets your RDS or Aurora endpoint, then creating a VPC endpoint service that points to that NLB. Once configured, you can follow the standard PrivateLink setup steps described above.

## IP allowlist (rare)

In most cases, PrivateLink eliminates the need for IP allowlisting since traffic flows through private connections. However, if you have a connection where one side uses PrivateLink and the other side requires IP allowlisting (for example, a public source connecting to a PrivateLink-enabled destination), you may need to allowlist Airbyte's IP addresses for the non-PrivateLink endpoint.

Contact Airbyte to obtain the current IP addresses for your region.
<!-- This is a different set of IPs from those we publicly document already. I think it's OK to publish, but check. -->
