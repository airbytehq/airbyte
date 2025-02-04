---
products: all
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Terraform Provider

[Terraform](https://www.terraform.io/), developed by HashiCorp, is an Infrastructure as Code (IaC) tool that empowers you to define and provision infrastructure using a declarative configuration language. If you already use Terraform to manage your infrastructure, you can use Airbyte's Terraform provider to automate and version control your Airbyte configuration as code. Airbyte's Terraform provider is built off [our API](https://reference.airbyte.com).

Follow this tutorial to learn to use Airbyte's Terraform Provider. If you don't need a tutorial, see the [Terraform provider reference docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs).

:::note
If you prefer videos, we also have [a series on YouTube](https://www.youtube.com/playlist?list=PLgyvStszwUHjdXjfaQl_-sYkW00dRsjW-). This article and the video series cover the same concepts, but the video series is older and a few things have changed since it was recorded.
:::

## Limitations and considerations

The Airbyte Terraform provider supports connectors available in **both** Self-Managed Community and Cloud. It doesn't support connectors that are only available in Self-Managed Community.

## Requirements before you begin

Before completing this tutorial, make sure you have the following.

- Basic familiarity with Terraform is helpful, but not required

- A code editor, like Visual Studio Code, with any of your preferred Terraform extensions installed

- [Terraform](https://developer.hashicorp.com/terraform/install) installed on your machine

- Access credentials:

    - For Cloud: [An API application](using-airbyte/configuring-api-access.md) in Airbyte, and your client ID and client secret.

    - For Self-Managed: your user name, password, and server URL.

## Step 1: Download and set up the provider

To begin, download the Terraform provider and configure it to run with your Airbyte instance.

1. Create a directory to house your Terraform project, navigate to it, and create a file called `main.tf`.

    ```bash
    mkdir terraform-airbyte
    cd terraform-airbyte
    touch main.tf
    ```

2. Go to https://registry.terraform.io/providers/airbytehq/airbyte/latest.

3. Click **Use Provider**, copy the code, and paste it into `main.tf`. It should look something like this:

    ```hcl title="main.tf"
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
        ```hcl title="main.tf"
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
        ```hcl title="main.tf"
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
        ```hcl title="variables.tf"
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
        ```hcl title="variables.tf"
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

## Important: Strongly versus weakly typed configurations {#typing}

Currently, the Airbyte provider offers two types of resources. There are benefits and drawbacks to both methods. Review this information before creating your sources and destinations.

### Strongly typed configurations

Resources with strongly typed configurations have strict rules about how configurations are written. If they're written incorrectly, these resources prevent `terraform apply` from running.

These resources depend on the underlying Airbyte connectors. Connectors are continually updated as third-party APIs change or we add new features. This creates two primary points of failure for Terraform.

- You upgrade the Terraform provider version, and fetch a new version of the config block. However, you do not upgrade your version of the connector in your Airbyte instance. The setup now crashes because there is a mismatch between the Terraform provider and the connector itself.

- The Terraform SDK is built at a given time. Then, the connector has a breaking change (for example, a third-party removes an API endpoint). You upgrade your connector, but now the Terraform provider hasn't been upgraded yet and doesn't work as expected.

Essentially, using this option creates an ongoing risk that upgrading the Terraform provider or a connector causes a breaking change.

### Weakly typed (JSON) configurations

Resources with weakly typed configurations use a JSON string to define how those configurations are written. These configurations are more robust when connectors change. Mismatches between a Terraform provider and a connector do not prevent `terraform apply` from running and may not cause any issues at all since the absence of a newly added configuration option might have no impact at all on your data and your use of that connector.

The main issue with this method is that JSON strings can technically contain anything, and you could make a mistake that Terraform doesn't warn you about. Currently, the best way to verify the correctness of your JSON string is to review the documentation for the strongly-typed resource for the source or destination you are creating.

:::note
We realize this process is undesirable, and are exploring ways to surface the right JSON string in a more obvious way.
:::

### How to choose

You can choose which type of resource you prefer. Airbyte generally recommends using a JSON configuration. Based on the feedback we receive, JSON causes less Terraform drift and makes upgrades less problematic.

## Step 2: Create a source

Now that Terraform is running, add a source from which you want to pull data.

You can choose between a strongly typed or weakly typed (JSON) configuration. See [Strongly versus weakly typed configurations](#typing) to learn which is better for you.

<Tabs>
    <TabItem value="Strongly typed" label="Strongly typed" default>
        ```hcl
        resource "airbyte_source_stripe" "my_source_stripe" {
            configuration = {
                sourceType = "stripe"
                account_id = "acct_123"
                client_secret = "sklive_abc"
                start_date = "2023-07-01T00:00:00Z"
                lookback_window_days = 0
                slice_range = 365
            }
            name = "Stripe"
            workspace_id = var.workspace_id
        }
        ```
    </TabItem>

    <TabItem value="JSON" label="JSON">
        asd
    </TabItem>
</Tabs>

## Step 3: Create a destination

Create a destination to which you want to sync your data.

## Step 4: Create a connection

Create a connection from your source to your destination.



## What's next?

When you're ready for Terraform to take control, our [Quickstarts repository](https://github.com/airbytehq/quickstarts) provides templates and shortcuts to help you build your data stack tailored to different domains like Marketing, Product, Finance, Operations, and more.
