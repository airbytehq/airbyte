# Instagram API

<HideInUI>

This page contains the setup guide and reference information for the [Instagram](https://www.instagram.com/) source connector.

</HideInUI>

## Prerequisites

- [Meta for Developers account](https://developers.facebook.com)
- [Instagram business account](https://www.facebook.com/business/help/898752960195806) to your
  Facebook page
- [Facebook App and Instagram Product](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/create-a-meta-app-with-instagram) (you'll
  use this to configure Instagram API as a source in Airbyte
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-platform/reference) to your Facebook app
- (Optional) [Business Login for Instagram](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/business-login)

## Setup guide

### Set up Instagram

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Instagram** from the **Source type** dropdown.
4. Enter a name for your source.
5. Enter **Access Token** generated
   using [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   or [by using an app you can create on Facebook](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started/)
   with the required permissions: instagram_basic, instagram_manage_insights, pages_show_list,
   pages_read_engagement.
6. (Optional) Enter the **Start Date** in YYYY-MM-DDTHH:mm:ssZ format. All data generated after this
   date will be replicated. If left blank, the start date will be set to 2 years before the present
   date.
7. Click **Set up source**.

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Instagram source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

:::note

Incremental sync modes are only available for
the [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
stream.

:::

## Supported Streams

The Instagram source connector supports the following streams. For more information, see
the [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)
and [Instagram Insights API documentation](https://developers.facebook.com/docs/instagram-api/guides/insights/).

- [User](https://developers.facebook.com/docs/instagram-api/reference/ig-user)
    - [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
- [Media](https://developers.facebook.com/docs/instagram-api/reference/ig-user/media)
    - [Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)
- [Stories](https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories/)
    - [Story Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

:::info
The Instagram connector syncs data related to Users, Media, and Stories and their insights from
the [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/). For performance data
related to Instagram Ads, use the Facebook Marketing source.
:::

### Entity-Relationship Diagram (ERD)
<EntityRelationshipDiagram></EntityRelationshipDiagram>

## Data type map

AirbyteRecords are required to conform to
the [Airbyte type](https://docs.airbyte.com/understanding-airbyte/supported-data-types/) system.
This means that all sources must produce schemas and records within these types and all destinations
must handle records that conform to this type system.

| Integration Type | Airbyte Type |
|:-----------------|:-------------|
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Instagram connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

Instagram limits the number of requests that can be made at a time. See
Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/#instagram-graph-api)
for more information.

### Troubleshooting

- Check out common troubleshooting issues for the Instagram API source connector on
  our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                              |
|:--------|:-----------|:-------------|:-------------------------------------|
| 0.1.0   | 2025-03-14 | [55852](https://github.com/airbytehq/airbyte/pull/55852)   | Add initial connector implementation |

</details>

</HideInUI>
