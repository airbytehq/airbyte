# September 2023

## airbyte v0.50.24 to v0.50.31

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

## ✨ Highlights

This month, we brought 4 new destinations to Airbyte focused on AI. This enables users to seamlessly flow data from 100s of our sources into large language models. Those four destinations are:

- [Qdrant](https://github.com/airbytehq/airbyte/pull/30332)
- [Choroma](https://github.com/airbytehq/airbyte/pull/30023)
- [Milvus](https://github.com/airbytehq/airbyte/pull/30023)
- [Pinecone](https://github.com/airbytehq/airbyte/pull/29539)

Another notable release was our new File CDK module within the [CDK](https://airbyte.com/connector-development-kit) for configuring and improving file-based connectors. This enables easier creation, maintenance, and improvement of file-base source connectors.

## Connector Improvements

We've also worked on several connector enhancements and additions. To name a few:

- [**Shopify**](https://github.com/airbytehq/airbyte/pull/29539) now fetches destroyed records, so that your source data is always reflected accurately
- [**Google Analytics**](https://github.com/airbytehq/airbyte/pull/30152) now allows for multiple Property IDs to be input, so that you can sync data from all your properties.
- [**Google Ads**](https://github.com/airbytehq/airbyte/pull/28970) now uses the change status to implement an improved incremental sync for Ad Groups and Campaign Criterion streams

Additionally, we added new streams for several connectors to bring in newly available API endpoints and adapt to user feedback, including:

- [**Github**](https://github.com/airbytehq/airbyte/pull/30823): Issue Timeline and Contributor Activity
- [**JIRA**](https://github.com/airbytehq/airbyte/pull/30755): Issue Types, Project Roles, and Issue Transitions
- [**Outreach**](https://github.com/airbytehq/airbyte/pull/30639): Call Purposes and Call Dispositions
- [**Zendesk**](https://github.com/airbytehq/airbyte/pull/30138): Articles
