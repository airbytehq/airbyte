# November 2023

## airbyte v0.50.34 to v0.50.35

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

## ✨ Highlights

Airbyte now supports extracting text content from PDF, Docx, and Pptx files from S3, Azure Blob Storage, and the newly introduced [Google Drive](/integrations/sources/google-drive.md) source. This is an important part of supporting LLM use cases that rely on unstructured data in files.

SSO and RBAC (admin roles only) are now available in Airbyte Cloud! Read more below.

## Platform Releases

- **SSO and RBAC** You can now use SSO in Airbyte Cloud to administer permissions in Airbyte. This is currently only available through Okta, with plans to support Active Directory next. We also now offer **RBAC** (admin roles only) to ensure a high level of security when managing you workspace. For access to this feature, reach out to our [Sales team](https://www.airbyte.com/company/talk-to-sales).
- **Continuous heartbeat checks** We're continually monitoring syncs to verify they continue making progress, and have added functionality in the background to ensure that we continue receiving updated ["heartbeat" messages](/understanding-airbyte/heartbeats.md) from our connectors. This will ensure that we continue delivering data and avoid any timeouts.

## Connector Improvements

In addition to being able to extract text content from unstructured data sources, we have also:

- Revamped core Marketing connectors Pinterest, Instagram and Klaviyo to significantly improve the setup experience and ensure resiliency and reliability.
- [Added incremenetal sync](https://github.com/airbytehq/airbyte/pull/32473) functionality for Hubspot's stream `property_history`, which improves sync time and reliability.
- [Added new streams](https://github.com/airbytehq/airbyte/pull/32738) for Amazon Seller Partner: `get_vendor_net_pure_product_margin_report`,`get_vendor_readl_time_inventory_report`, and `get_vendor_traffic_report` to enable additional reporting.
- Released our first connector, Stripe, that can perform [concurrent syncs](https://github.com/airbytehq/airbyte/pull/32473) where streams sync in parallel when syncing in Full Refresh mode.
