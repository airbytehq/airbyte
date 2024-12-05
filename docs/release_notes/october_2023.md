# October 2023

## airbyte v0.50.31 to v0.50.33

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

## ✨ Highlights

With lightning-fast replication speeds of over 10 MB per second, incremental CDC syncs and more resumable snapshots, we've redefined what you can expect in terms of speed and reliability when replicating data from both [MySQL](https://airbyte.com/blog/behind-the-performance-improvements-of-our-mysql-source) and [MongoDB](https://airbyte.com/blog/10-mb-per-second-incremental-mongodb-syncs) databases.

In [v0.50.31](https://github.com/airbytehq/airbyte-platform/releases/tag/v0.50.31), we also released [versioned Connector Documentation](https://github.com/airbytehq/airbyte/pull/30410), which allows everyone to see the correct version of the documentation for their connector version without needing to upgrade their Airbyte platform version.

We're also always learning and listening to user feedback. We no longer [deduplicate raw tables](https://github.com/airbytehq/airbyte/pull/31520) to further speed up syncs with Destinations V2. We also released a new voting feature on our [docs](https://docs.airbyte.com) that asks how helpful our docs are for you.

This month, we also held our annual Hacktoberfest, from which we have already merged 51 PRs and welcomed 3 new contributors to our community!

## Platform Releases

- **Enhanced payment options:** Cloud customers can now sign up for [auto-recharging of their balance](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-credits#automatic-reload-of-credits-beta) and can purchase up to 6,000 credits within our application.
- **Free historical syncs:** Cloud customers can have more predictability around pricing with free historical syncs for any new connector. Reach out to our Sales team if interested.
- **Email Notification Recipient** Cloud customers can now designate the recipient of important email notifications about their connectors and syncs.

## Connector Improvements

Many of our enhancements came from our Community this month as a part of our Hacktoberfest. Notably, we enhanced the connector experience by:

- [**GitLab**](https://github.com/airbytehq/airbyte/pull/31492) now gracefully handles the expiration of access tokens
- [**Orbit**](https://github.com/airbytehq/airbyte/pull/30138) and [**Qualaroo**](https://github.com/airbytehq/airbyte/pull/30138) were migrated to low-code, which improves the maintainability of the connector (thanks to community member Aviraj Gour!)
- [**Pipdrive**](https://github.com/airbytehq/airbyte/pull/30138): optimized custom fields, which are commonly found in this connector.

Additionally, we added new streams for several connectors to ensure users have access to all their data, including:

- [**Chargify**](https://github.com/airbytehq/airbyte/pull/31116): Coupons, Transactions, and Invoices
- [**Mailchimp**](https://github.com/airbytehq/airbyte/pull/31922): Segment and Unsubscribes
- [**Pipedrive**](https://github.com/airbytehq/airbyte/pull/31885): Mails (thanks to community member Tope Folorunso!) and Goals
- [**Asana**](https://github.com/airbytehq/airbyte/pull/31634): Events, Attachments, OrganizationExports (thanks to Tope again!)
- [**Tiktok Ads**](https://github.com/airbytehq/airbyte/pull/31610): Audiences, Images, Music, Portfolios, Videos, Ad Audiences Report by Province
- [**Square**](https://github.com/airbytehq/airbyte/pull/30138): Bank Accounts (thanks community member Aviraj Gour) and Cash Drawers
- [**Notion**](https://github.com/airbytehq/airbyte/pull/30324): Blocks, Pages and Comments
