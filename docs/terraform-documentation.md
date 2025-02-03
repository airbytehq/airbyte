---
products: all
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Terraform Provider

[Terraform](https://www.terraform.io/), developed by HashiCorp, is an Infrastructure as Code (IaC) tool that empowers you to define and provision infrastructure using a declarative configuration language. If you already use Terraform to manage your infrastructure, you can use Airbyte's Terraform provider to automate and version control your Airbyte configuration as code. Airbyte's Terraform provider is built off [our API](https://reference.airbyte.com).

Terraform can help you:

- Save time managing Airbyte 

- Collaborate on configuration changes with your teammates

- Preserve a history of changes to your configuration to improve audits and diagnose problems with your data

- Control data connectors as infrastructure, just as you do your cloud environment

## Limitations and considerations

The Airbyte Terraform provider supports connectors available in **both** Self-Managed Community and Cloud. It doesn't support connectors that are only available in Self-Managed Community.

## Get started with Airbyte's Terraform Provider

Follow this simple tutorial to learn to use Airbyte's Terraform Provider.

:::note
If you prefer videos, we also have [a series on YouTube](https://www.youtube.com/playlist?list=PLgyvStszwUHjdXjfaQl_-sYkW00dRsjW-). This article and the video series cover the same concepts, but the video series is older and a few things have changed since it was recorded.
:::

### Requirements before you begin

Before completing this tutorial, make sure you have the following.

- Basic familiarity with Terraform is helpful, but not required.

- A code editor, like Visual Studio Code

- [Terraform](https://developer.hashicorp.com/terraform/install) installed on your machine

- Access credentials:

    - For Cloud: [An API application](using-airbyte/configuring-api-access.md) in Airbyte, and your client ID and client secret.

    - For Self-Managed: your user name, password, and server URL.

### Step 1: Download and set up the provider

To begin, download the Terraform provider and configure it to run with your Airbyte instance.

1. Create a directory to house your Terraform project, navigate to it, and create a file called `main.tf`.

    ```bash
    mkdir terraform-airbyte
    cd terraform-airbyte
    touch main.tf
    ```

2. Go to https://registry.terraform.io/providers/airbytehq/airbyte/latest.

3. Click **Use Provider**, copy the code, and paste it into `main.tf`. It should look something like this:

    ```tf title="main.tf"
    terraform {
        required_providers {
            airbyte = {
            source = "airbytehq/airbyte"
            version = "0.6.5"
            }
        }
    }

    provider "airbyte" {
        # Configuration options
    }
    ```

4. Configure the Airbyte provider to use your credentials. **Don't put your sensitive data into `main.tf`**. Instead, insert variables that you'll populate later.

    <Tabs>
    <TabItem value="Cloud" label="Cloud" default>
        ```tf title="main.tf"
        terraform {
            required_providers {
                airbyte = {
                source = "airbytehq/airbyte"
                version = "0.6.5"
                }
            }
        }

        provider "airbyte" {
            // highlight-start
            client_id = var.client_id
            client_secret = var.client_secret
            // highlight-end
        }
        ```
    </TabItem>
    <TabItem value="Self-Managed" label="Self-Managed">
        ```tf title="main.tf"
        terraform {
            required_providers {
                airbyte = {
                source = "airbytehq/airbyte"
                version = "0.6.5"
                }
            }
        }

        provider "airbyte" {
            // highlight-start
            password = var.password
            username = var.username

            # Only if running locally
            server_url = "http://localhost:8000/api/public/v1/"
            // highlight-end
        }
        ```
    </TabItem>
    </Tabs>

5. In your terminal, create a file called `variables.tf`. This file stores sensitive variables that you don't want to appear in `main.tf`.

    ```bash
    touch variables.tf
    ```

6. Populate `variables.tf` and define your variables.

    <Tabs>
    <TabItem value="Cloud" label="Cloud" default>
        ```tf title="variables.tf"
        variable "client_id" {
            type = string
            default = "YOUR_CLIENT_ID"
        }

        variable "client_secret" {
            type = string
            default = "YOUR_CLIENT_SECRET"
        }
        ```
    </TabItem>
    <TabItem value="Self-Managed" label="Self-Managed">
        ```tf title="variables.tf"
        variable "username" {
            type = string
            default = "YOUR_USER_NAME"
        }

        variable "password" {
            type = string
            default = "YOUR_PASSWORD"
        }
        ```
    </TabItem>
    </Tabs>

7. Run `terraform init`. Terraform tells you it initialized successfully. If it didn't, check your code against the code samples above.

8. Run `terraform plan`. Terraform tells you there are no changes.

9. Run `terraform apply`. Terraform tells you there are no changes.

### Step 2: Create a source

Now that Terraform is running, add a source from which you want to pull data.

### Step 3: Create a destination

Create a destination to which you want to sync your data.

### Step 4: Create a connection

Create a connection from your source to your destination.

## Strongly-typed versus JSON configurations

Currently, the Airbyte provider offers two types of resources. There are benefits and drawbacks to both methods.

### Strongly-typed configurations
- Strongly-typed configurations

### JSON configurations
- JSON configurations

### How to choose

Right now, you can choose which type of resource you prefer. Airbyte generally recommends using a JSON configuration. Based on the feedback we receive, JSON seems to cause less Terraform drift and make provider upgrades less problematic.

## What's next?

When you're ready for Terraform to take control, our [Quickstarts repository](https://github.com/airbytehq/quickstarts) provides templates and shortcuts to help you build your data stack tailored to different domains like Marketing, Product, Finance, Operations, and more.
