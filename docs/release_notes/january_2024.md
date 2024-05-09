# January 2024

## airbyte v0.50.41 to v0.50.45

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

## ✨ Highlights

Airbyte migrated our [Redshift destination](https://github.com/airbytehq/airbyte/pull/34077) on the [Destinations V2](./upgrading_to_destinations_v2) framework. This enables you to map tables one-to-one with your source, experience better error handling, and deliver data incrementally.

## Connector Improvements

In addition to our Redshift V2 destination, we also released a few notable Connector improvements:

- Our S3 Source now supports [IAM role-based authentication](https://github.com/airbytehq/airbyte/pull/33818), allowing users to utilize IAM roles for more granular control over permissions and to eliminate the need for managing static access keys.
- Our [Salesforce](https://github.com/airbytehq/airbyte/issues/30819) source now supports syncing the object ContentDocumentLink, which enables reporting for files within Content Documents.
- [OneDrive](https://docs.airbyte.com/integrations/sources/microsoft-onedrive) and [Sharepoint](https://github.com/airbytehq/airbyte/pull/33537) are now offered as a source from which to connect your files.
- Stripe and Salesforce are enabled to run [concurrently](https://github.com/airbytehq/airbyte/pull/34454) with full refresh with 4x speed
