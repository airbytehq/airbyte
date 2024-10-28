# February 2024

## airbyte v0.50.46 to v0.50.54

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

## ✨ Highlights

Airbyte migrated our [Postgres destination](https://github.com/airbytehq/airbyte/pull/35042) to the [Destinations V2](./upgrading_to_destinations_v2) framework. This enables you to map tables one-to-one with your source, experience better error handling, and deliver data incrementally.

## Platform Releases

- **Read-only Users** You can now enable read-only users in Airbyte Cloud (with Teams add-on) or Self-Managed Enterprise to administer read-only permissions in Airbyte. For access to this feature, reach out to our [Sales team](https://www.airbyte.com/company/talk-to-sales).

- Our Slack and Email (for Cloud only) notifications have received a facelift! Additional contextual information about sync failures or schema changes are now included in the notification to ensure you can act on any pipeline changes quickly.

## Connector Improvements

In addition to our Postgres V2 destination, we also released a few notable Connector improvements:

- Our [Paypal source](https://github.com/airbytehq/airbyte/pull/34510) has been rigorously tested for bugs and now syncs new streams `Catalog Products`, `Disputes`, `Invoicing`, `Orders`, `Payments` and `Subscriptions`.
- [Chargebee](https://github.com/airbytehq/airbyte/pull/34053) source now syncs incrementally for `unbilled-charge`, `gift`, and `site_migration_detail`
- We launched [PyAirbyte](/using-airbyte/pyairbyte/getting-started.mdx), a new interface to use Airbyte connectors with for Python developers.
