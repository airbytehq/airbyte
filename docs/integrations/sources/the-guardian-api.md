# The Guardian API

## Overview

The Guardian API source can sync data from the [The Guardian](https://open-platform.theguardian.com/)

## Requirements

To access the API, you will need to sign up for an API key, which should be sent with every request. Visit [this](https://open-platform.theguardian.com/access) link to register for an API key.

The following (optional) parameters can be provided to the connector :-

---

##### `q` (query)

The `q` (query) parameter filters the results to only those that include that search term. The `q` parameter supports `AND`, `OR` and `NOT` operators. For example, let's see if the Guardian has any content on political debates: `https://content.guardianapis.com/search?q=debates`

Here the q parameter filters the results to only those that include that search term. In this case, there are many results, so we might want to filter down the response to something more meaningful, specifically looking for political content published in 2014, for example: `https://content.guardianapis.com/search?q=debate&tag=politics/politics&from-date=2014-01-01&api-key=test`

---

##### `tag`

A tag is a piece of data that is used to categorise content. All Guardian content is manually categorised using these tags, of which there are more than 50,000. Use this parameter to filter results by showing only the ones matching the entered tag. See <a href="https://content.guardianapis.com/tags?api-key=test">here</a> for a list of all tags, and <a href="https://open-platform.theguardian.com/documentation/tag">here</a> for the tags endpoint documentation.

---

##### `section`

Use this to filter the results by a particular section. See <a href="https://content.guardianapis.com/sections?api-key=test">here</a> for a list of all sections, and <a href="https://open-platform.theguardian.com/documentation/section">here</a> for the sections endpoint documentation.

---

##### `order-by`

Use this to sort the results. The three available sorting options are - newest, oldest, relevance. For enabling incremental syncs set order-by to oldest.

---

##### `start_date`

Use this to set the minimum date (YYYY-MM-DD) of the results. Results older than the start_date will not be shown.

---

##### `end_date`

Use this to set the maximum date (YYYY-MM-DD) of the results. Results newer than the end_date will not be shown.
Default is set to the current date (today) for incremental syncs.

---

## Output schema

#### Each content item (news article) has the following structure:-

```yaml
{
    "id": "string",
    "type": "string"
    "sectionId": "string"
    "sectionName": "string"
    "webPublicationDate": "string"
    "webTitle": "string"
    "webUrl": "string"
    "apiUrl": "string"
    "isHosted": "boolean"
    "pillarId": "string"
    "pillarName": "string"
}
```

The source is capable of syncing the content stream.

## Setup guide

## Step 1: Set up the The Guardian API connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, select **The Guardian API** from the Source type dropdown.
4. Enter your api_key (mandatory) and any other optional parameters as per your requirements.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source (The Guardian API).
3. Enter your api_key (mandatory) and any other optional parameters as per your requirements.
4. Click **Set up source**.

## Supported sync modes

The Guardian API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Performance considerations

The key that you are assigned is rate-limited and as such any applications that depend on making large numbers of requests on a polling basis are likely to exceed their daily quota and thus be prevented from making further requests until the next period begins.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                        |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------- |
| 0.2.0   | 2024-09-06 | [45195](https://github.com/airbytehq/airbyte/pull/45195) | Refactor connector to manifest-only format     |
| 0.1.9   | 2024-08-31 | [44997](https://github.com/airbytehq/airbyte/pull/44997) | Update dependencies                            |
| 0.1.8   | 2024-08-24 | [44746](https://github.com/airbytehq/airbyte/pull/44746) | Update dependencies                            |
| 0.1.7   | 2024-08-17 | [44208](https://github.com/airbytehq/airbyte/pull/44208) | Update dependencies                            |
| 0.1.6   | 2024-08-10 | [43540](https://github.com/airbytehq/airbyte/pull/43540) | Update dependencies                            |
| 0.1.5   | 2024-08-03 | [42781](https://github.com/airbytehq/airbyte/pull/42781) | Update dependencies                            |
| 0.1.4   | 2024-07-20 | [42316](https://github.com/airbytehq/airbyte/pull/42316) | Update dependencies                            |
| 0.1.3   | 2024-07-13 | [41878](https://github.com/airbytehq/airbyte/pull/41878) | Update dependencies                            |
| 0.1.2   | 2024-07-10 | [41505](https://github.com/airbytehq/airbyte/pull/41505) | Update dependencies                            |
| 0.1.1   | 2024-07-10 | [41049](https://github.com/airbytehq/airbyte/pull/41049) | Migrate to poetry                              |
| 0.1.0   | 2022-10-30 | [18654](https://github.com/airbytehq/airbyte/pull/18654) | 🎉 New Source: The Guardian API [low-code CDK] |

</details>
