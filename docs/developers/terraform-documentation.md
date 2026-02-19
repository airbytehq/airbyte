---
products: all
---

# Terraform provider

[Terraform](https://www.terraform.io/), developed by HashiCorp, is an Infrastructure as Code (IaC) tool that empowers you to define and provision infrastructure using a declarative configuration language. If you use Terraform to manage your infrastructure, you can use Airbyte's Terraform provider to automate and version control your Airbyte configuration as code. Airbyte's Terraform provider is built off [Airbyte's API](https://reference.airbyte.com).

## Documentation

The Airbyte Terraform provider documentation lives on the [Terraform Registry](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs), which is the source of truth for all provider reference docs, guides, and examples.

| Resource | Description |
|----------|-------------|
| [Getting Started guide](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs/guides/getting_started) | Set up the provider and create your first source, destination, and connection. |
| [Provider reference](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs) | Provider configuration, authentication, and schema. |
| [Resource and data source docs](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs/resources/source) | Full reference for all resources and data sources. |
| [Migrating to 1.0](https://registry.terraform.io/providers/airbytehq/airbyte/latest/docs/guides/v1_migration_guide) | Upgrade from typed connector-specific resources to the generic `airbyte_source` / `airbyte_destination` resources. |

## Additional resources

- [Airbyte API reference](https://reference.airbyte.com) — The API that powers the Terraform provider.
- [API access configuration](/platform/using-airbyte/configuring-api-access) — Set up API credentials for the Terraform provider.
- [Pre-1.0 getting started tutorial](terraform-provider-pre-1.0) — Reference for users on provider versions before 1.0.
