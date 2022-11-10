# Appfollow

This page guides you through setting up the Appfollow source connector to sync data for the [Appfollow API](https://appfollow.docs.apiary.io/#introduction/api-methods).

## Prerequisite

To set up the Appfollow source connector, you'll need your Appfollow `ext_id`, `cid`, `api_secret` and `Country`.

## Set up the Appfollow source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Appfollow** from the Source type dropdown.
4. Enter a name for your source.
5. For **ext_id**, **cid**, **api_secret** and **Country**, enter the Appfollow ext_id, cid, api_secret and country.
6. Click **Set up source**.

## Supported Streams

The Appfollow source connector supports the following streams:

- [Ratings](https://appfollow.docs.apiary.io/#reference/0/9.-ratings) \(Full Refresh sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Supported sync modes

The Appfollow source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Performance considerations

The Appfollow connector ideally should gracefully handle Appfollow API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject               |
| :------ | :--------- | :------------------------------------------------------- | :-------------------- |
| 0.1.0   | 2022-08-11 | [14418](https://github.com/airbytehq/airbyte/pull/14418) | New Source: Appfollow |
