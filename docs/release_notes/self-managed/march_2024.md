# March 2024

## airbyte v0.51.0 to v0.56.0

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

## ✨ Highlights

Airbyte now supports **OpenID Connect (OIDC) SSO** for Airbyte Enterprise and Airbyte Cloud Teams. This enables companies to use Airbyte with Entra ID/AD via the OIDC protocol.

Airbyte certified our [Microsoft SQL Server source](/integrations/sources/mssql) to support terabyte-sized tables, expanded datetime data types, and reliability improvements.

Airbyte migrated our [Redshift destination](https://github.com/airbytehq/airbyte/pull/36255) to the [Destinations V2](./upgrading_to_destinations_v2) framework. This enables you to map tables one-to-one with your source, experience better error handling (particularly with large records), and deliver data incrementally.

## Platform Releases

In addition to our OpenID Connect support, we also released:

- A major upgrade to our Docker and Helm deployments, which simplifies how external logs are configured.

- A breaking change to Docker deployments. Containers no longer run as the `root` user. If you are upgrading from an older version, the `airbyte_workspace` docker volume must be recreated to fix the ownership of staging directories under `/tmp` (in the container). Alternatively, you can manually update the ownership (`airbyte:airbyte`) of the directory mount point /tmp/workspace in all containers where `airbyte_workspace` is mounted (see: `docker-compose.yaml`)

- Our major version upgrades (Airbyte Cloud only) now only require manual upgrading when you are actively syncing a stream that has changed. Otherwise, syncs will continue as is and the version will be upgraded automatically for you.

## Connector Improvements

In addition to our MS-SQL certification, we also released a few notable Connector improvements:

- We released several connector builder enhancements, including support for raw YAML blocks, modification the start date when testing, and added the ability to adjust page/slice/record limits. We also resolved bugs in page size and interpolation inputs, improved the switching time between YAML and UI, and fixed several layout issues.
- Our [Bing source](https://github.com/airbytehq/airbyte/pull/35812) includes the following new streams: `Audience Performance Report`, `Goals And Funnels Report`, `Product Dimension Performance Report`
- Our [JIRA source](https://github.com/airbytehq/airbyte/pull/35656) now contains more fields to the following streams: `board_issues`,`filter_sharing`,`filters`,`issues`, `permission_schemes`, `sprint_issues`,`users_groups_detailed` and `workflows`
- Our [Snapchat Source](https://github.com/airbytehq/airbyte/pull/35660) now contains additional fields in the `ads`, `adsquads`, `creatives`, and `media` streams.
