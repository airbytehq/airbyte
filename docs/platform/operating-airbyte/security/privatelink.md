---
products: cloud
---

# PrivateLink

AWS PrivateLink allows Airbyte Cloud to securely connect to your data sources and destinations without exposing them to the public internet. Traffic between Airbyte and your resources stays entirely within AWS's private network, providing enhanced security for organizations with strict network isolation requirements.

## Benefits of Using PrivateLink

PrivateLink offers several advantages for security-conscious organizations:

- **No public IP exposure**: Your data sources and destinations remain completely private. There's no need to assign public IP addresses or open firewall rules to the internet.

- **Traffic stays on AWS's network**: All data transferred between Airbyte and your resources travels through AWS's private backbone, never traversing the public internet.

- **Simplified network security**: Instead of managing complex firewall rules and IP allowlists, you control access through AWS's native VPC endpoint service permissions.

- **Reduced attack surface**: By eliminating public endpoints, you reduce the potential vectors for unauthorized access to your data infrastructure.

## How It Works

## Prerequisites

## Supported Regions

## Setting Up PrivateLink

### Step 1: Contact Airbyte

### Step 2: Create a VPC Endpoint Service

### Step 3: Configure Permissions for Airbyte

### Step 4: Provide Your Endpoint Service Name to Airbyte

## Using PrivateLink with Managed AWS Services

## IP Allowlisting (Optional)

## Security Model

## Limitations

## FAQ
