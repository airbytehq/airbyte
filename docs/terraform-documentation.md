---
products: all
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Terraform Provider

[Terraform](https://www.terraform.io/), developed by HashiCorp, is an Infrastructure as Code (IaC) tool that empowers you to define and provision infrastructure using a declarative configuration language. If you already use Terraform to manage your infrastructure or want to start doing this, you can use Airbyte's Terraform provider to automate and version control your Airbyte configuration as code. Airbyte's Terraform provider is built off [our API](https://reference.airbyte.com).

Follow this tutorial to learn to use Airbyte's Terraform Provider. If you don't need a tutorial, see the [Terraform provider reference docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs).

:::note
If you prefer videos, we also have [a series on YouTube](https://www.youtube.com/playlist?list=PLgyvStszwUHjdXjfaQl_-sYkW00dRsjW-). This article and the video series cover the same concepts, but the video series is older and a few things have changed since it was recorded.
:::

## Limitations and considerations

The Airbyte Terraform provider supports connectors available in **both** Self-Managed Community and Cloud. It doesn't support connectors that are only available in Self-Managed Community.

## Requirements before you begin

Before completing this tutorial, make sure you have the following.

- Basic familiarity with Terraform is helpful, but not required

- A code editor, like Visual Studio Code, optionally with a Terraform extension installed

- [Terraform](https://developer.hashicorp.com/terraform/install) installed on your machine

- Airbyte credentials:

    - For Cloud: [An API application](using-airbyte/configuring-api-access.md) in Airbyte, and your client ID and client secret.

    - For Self-Managed: your user name, password, and server URL.

    - Your workspace ID. To get your workspace ID, open your workspace in Airbyte, then copy the ID from the URL. It looks like: `039da657-f061-493e-a836-9bce86bc5e35`.

- Source and destination credentials. This tutorial uses [Stripe](integrations/sources/stripe) and [BigQuery](integrations/destinations/bigquery), but you can substitute any other connector. Consult the documentation for those connectors to ensure you are ready to connect.

## Step 1: Set up the Terraform provider

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

        variable "workspace_id" {
            type = string
            default = "YOUR_AIRBYTE_WORKSPACE_ID"
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

        variable "workspace_id" {
            type = string
            default = "YOUR_AIRBYTE_WORKSPACE_ID"
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

Resources with strongly typed configuration objects have strict rules about how configurations are written. If they're written incorrectly, these resources prevent `terraform apply` from running.

These resources depend on the underlying Airbyte connectors. Connectors are continually updated as third-party APIs change or we add new features. This creates two primary points of failure for Terraform.

- You upgrade the Terraform provider version, and fetch a new version of the config block. However, you do not upgrade your version of the connector in your Airbyte instance. The setup now crashes because there is a mismatch between the Terraform provider and the connector itself.

- The Terraform SDK is built at a given time. Then, the connector has a breaking change (for example, a third-party removes an API endpoint). You upgrade your connector, but now the Terraform provider hasn't been upgraded yet and doesn't work as expected.

Essentially, using this option creates an ongoing risk that upgrading the Terraform provider or a connector causes a breaking change.

### Weakly typed (JSON) configurations

Resources with weakly typed configurations use a JSON string to define how those configurations are written. These configurations are more robust when connectors change. Mismatches between a Terraform provider and a connector do not prevent `terraform apply` from running. The absence of a newly added configuration option might have no impact at all on your data and your use of that connector.

The main issue with this method is that JSON strings can technically contain anything, and you could make a mistake that Terraform doesn't warn you about. Currently, the best way to verify the correctness of your JSON string is to review the documentation for the strongly-typed resource for the source or destination you are creating.

:::note
We realize this method for getting the JSON string is undesirable, and are exploring ways to surface the right JSON string in a more obvious way.
:::

### How to choose

- For Airbyte and Marketplace connectors, you can choose which type of resource you prefer. Airbyte generally recommends using a JSON configuration. Based on the feedback we receive, JSON causes less Terraform drift and makes upgrades less problematic in the long run.

- For custom connectors, only weakly typed JSON configurations are possible.

## Step 2: Create a source

Add a source from which you want to pull data. In this example, you add Stripe as a source. If you want to use a different source, you can find the code sample for the corresponding resource in the [Terraform provider reference docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs).

1. Add your source to `main.tf`.

    <Tabs>
    <TabItem value="Strongly typed" label="Strongly typed" default>
        ```hcl title="main.tf"
        resource "airbyte_source_stripe" "my_source_stripe" {
            configuration = {
                sourceType = "stripe"
                account_id = "YOUR_STRIPE_ACCOUNT_ID"
                client_secret = "YOUR_STRIPE_CLIENT_SECRET"
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
        
        For this and any other Airbyte or Marketplace connector, you can define the source type in the JSON string.
        
        ```hcl title="main.tf"
        resource "airbyte_source_custom" "my_source_stripe" {
            configuration = jsonencode({
                sourceType = "stripe",
                "account_id" = "YOUR_STRIPE_ACCOUNT_ID",
                "client_secret" = "YOUR_STRIPE_CLIENT_SECRET",
                "start_date" = "2023-07-01T00:00:00Z",
                "lookback_window_days" = 0,
                "slice_range" = 365
                })
            name = "Stripe"
            workspace_id = var.workspace_id
        }
        ```

        If this is your own custom connector, use `definition_id` to define the source type. To get this value, open your custom connector in Airbyte and copy it from the URL of that connector.

        ```hcl title="main.tf"
        resource "airbyte_source_custom" "my_source_stripe" {
            configuration = jsonencode({
                "account_id" = "YOUR_STRIPE_ACCOUNT_ID",
                "client_secret" = "YOUR_STRIPE_CLIENT_SECRET",
                "start_date" = "2023-07-01T00:00:00Z",
                "lookback_window_days" = 0,
                "slice_range" = 365
                })
            name = "Stripe"
            workspace_id = var.workspace_id
            // highlight-next-line
            definition_id = "e094cb9a-26de-4645-8761-65c0c425d1de"
        }
        ```

    </TabItem>
    </Tabs>

2. Run `terraform apply`. Terraform tells you it will add 1 resource. Type `yes` and press <kbd>Enter</kbd>.

Terraform adds the source to Airbyte. To see your new source, open your Airbyte workspace and and click **Sources**. Or, use the [List sources](https://reference.airbyte.com/reference/listsources) API endpoint.

## Step 3: Create a destination

Add a destination to which you want to push data. In this example, you add BigQuery as a destination. If you want to use a different destination, you can find the code sample for the corresponding resource in the [Terraform provider reference docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs).

1. Add your destination to `main.tf`.

    :::important
    For BigQuery, you must use a service account with credentials provided as a JSON string (required for Cloud, but technically optional for self-managed). It's extremely helpful to wrap your credentials JSON in [jsonencode](https://developer.hashicorp.com/terraform/language/functions/jsonencode), like these examples do. This prevents you from having to manually escape slashes and newlines in your credentials and leaves your Terraform code more human-readable.
    :::

    <Tabs>
    <TabItem value="Strongly typed" label="Strongly typed" default>

        ```hcl title="main.tf"
        resource "airbyte_destination_bigquery" "my_destination_bigquery" {
            configuration = {
                destination_type       = "BigQuery"
                credentials_json       = jsonencode({
                    "type"                        = "service_account",
                    "project_id"                  = "YOUR_PROJECT_ID",
                    "private_key_id"              = "YOUR_PRIVATE_KEY_ID",
                    "private_key"                 = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
                    "client_email"                = "you@example.iam.gserviceaccount.com",
                    "client_id"                   = "YOUR_CLIENT_ID",
                    "auth_uri"                    = "https://accounts.google.com/o/oauth2/auth",
                    "token_uri"                   = "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url" = "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url"        = "https://www.googleapis.com/robot/v1/metadata/x509/you@example.iam.gserviceaccount.com"
                })
                dataset_id              = "YOUR_DATASET_ID"
                dataset_location        = "us-central1"
                project_id              = "YOUR_PROJECT_ID"
                transformation_priority = "batch"
            }
            name         = "BigQuery"
            workspace_id = var.workspace_id
        }
        ```

    </TabItem>

    <TabItem value="JSON" label="JSON">
            
        ```hcl title="main.tf"
        resource "airbyte_destination_custom" "my_destination_bigquery_custom" {
            configuration = jsonencode({ 
                "destination_type"                = "BigQuery"
                "credentials_json" = jsonencode({
                    "type"                        = "service_account",
                    "project_id"                  = "YOUR_PROJECT_ID",
                    "private_key_id"              = "YOUR_PRIVATE_KEY_ID",
                    "private_key"                 = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
                    "client_email"                = "you@example.iam.gserviceaccount.com",
                    "client_id"                   = "YOUR_CLIENT_ID",
                    "auth_uri"                    = "https://accounts.google.com/o/oauth2/auth",
                    "token_uri"                   = "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url" = "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url"        = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project.iam.gserviceaccount.com"
                }),
                "dataset_id"                      = "YOUR_DATASET_ID",
                "dataset_location"                = "us-central1",
                "project_id"                      = "YOUR_PROJECT_ID",
                "transformation_priority"         = "batch"
            })
            name                  = "BigQuery"
            workspace_id          = var.workspace_id
        }
        ```

    </TabItem>
    </Tabs>

    :::note
    Destinations have many more optional attributes. For simplicity, this tutorial uses defaults. See the [reference docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs/resources/destination_bigquery) for additional attributes.
    :::

2. Run `terraform apply`. Terraform tells you it will add 1 resource. Type `yes` and press <kbd>Enter</kbd>.

Terraform adds the destination to Airbyte. To see your new destination, open your Airbyte workspace and and click **Destinations**. Or, use the [List destinations](https://reference.airbyte.com/reference/listdestinations) API endpoint.

## Step 4: Create a connection

Create a connection from your source to your destination.

1. Add your connection to `main.tf` using the [Airbyte connection](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs/resources/connection) resource.

    ```hcl title="main.tf"
    resource "airbyte_connection" "stripe_to_bigquery" {
        name           = "Stripe to BigQuery"
        source_id      = airbyte_source_stripe.my_source_stripe.source_id
        destination_id = airbyte_destination_bigquery.my_destination_bigquery.destination_id
    }
    ```

    This example connection will not sync automatically. The [reference docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs/resources/connection) describe a number of attributes you can use to schedule how and when your connections sync.

2. Run `terraform apply`. Terraform tells you it will add 1 resource. Type `yes` and press <kbd>Enter</kbd>.

Terraform adds the connection to Airbyte. To see your new connection, open your Airbyte workspace and click **Connections**. Or, use the [List connections](https://reference.airbyte.com/reference/listconnections) API endpoint.

## What's next?

Congratulations! You created your first source, your first destination, and a connection between the two.

- Continue building your sources, destinations, and connections for all your data using our [Terraform docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs).

- Check out the [Quickstarts repository](https://github.com/airbytehq/quickstarts). It's full of templates and shortcuts to help you build common data stacks using Terraform and Python.
