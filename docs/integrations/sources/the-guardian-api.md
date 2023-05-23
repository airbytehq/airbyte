# The Guardian API

## Overview

The Guardian API source can sync data from [The Guardian](https://open-platform.theguardian.com/).

## Requirements

Before setting up the The Guardian API connector, you will need to sign up for an API key. Your API key should be sent with every request. To register for an API key, visit [this](https://open-platform.theguardian.com/access) link.

The following (optional) parameters can be provided to the connector:

---

##### `q` (query)

The `q` (query) parameter filters the results to only those that include the specified search term. The `q` parameter supports `AND`, `OR`, and `NOT` operators. For example, to see if The Guardian has any content on political debates, use this endpoint: `https://content.guardianapis.com/search?q=debates`.

Here the `q` parameter filters the results to only those that include the search term. In this case, there are many results, so you might want to filter down the response to something more meaningful, specifically looking for political content published in 2014. To filter for this, use this endpoint: `https://content.guardianapis.com/search?q=debate&tag=politics/politics&from-date=2014-01-01&api-key=test`.

---

##### `tag`

A tag is a piece of data that is used to categorize content. All Guardian content is manually categorized using these tags, of which there are more than 50,000. Use this parameter to filter results by showing only the ones matching the entered tag. See [here](https://content.guardianapis.com/tags?api-key=test) for a list of all tags, and [here](https://open-platform.theguardian.com/documentation/tag) for the tags endpoint documentation.

---

##### `section`

Use this to filter the results by a particular section. See [here](https://content.guardianapis.com/sections?api-key=test) for a list of all sections and [here](https://open-platform.theguardian.com/documentation/section) for the sections endpoint documentation.

---

##### `order-by`

Use this to sort the results. You can choose from the following three sorting options: newest, oldest, and relevance. For enabling incremental syncs, set order-by to oldest.

---

##### `start_date`

Use this to set the minimum date (YYYY-MM-DD) of the results. Results older than the start_date will not be shown.

---

##### `end_date`

Use this to set the maximum date (YYYY-MM-DD) of the results. Results newer than the end_date will not be shown. By default, the current date (today) is set for incremental syncs.

## Output schema

The The Guardian API source is capable of syncing the content stream. Each content item (news article) has the following structure:

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

## Setup guide

## Step 1: Set up the The Guardian API connector in Airbyte

### For Airbyte Cloud:

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, select **The Guardian API** from the Source type dropdown.
4. Enter the `api_key` parameter, which is mandatory. 
5. Enter any other optional parameters as per your requirements.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source (The Guardian API).
3. Enter the `api_key` parameter, which is mandatory. 
4. Enter any other optional parameters as per your requirements.
5. Click **Set up source**.

## Connector configuration

```json
{
  "api_key": {
      "title": "API Key",
      "type": "string",
      "description": "Your API Key. The key is case sensitive in nature. See the API documentation for more details.",
      "airbyte_secret": true
  },
  "start_date": {
      "title": "Start Date",
      "type": "string",
      "description": "Use this to set the minimum date (YYYY-MM-DD) of the results. Results older than the start_date will not be shown.",
      "pattern": "^([1-9][0-9]{3})\\-(0?[1-9]|1[012])\\-(0?[1-9]|[12][0-9]|3[01])$",
      "examples": [
          "YYYY-MM-DD"
      ]
  },
  "query": {
      "title": "Query",
      "type": "string",
      "description": "(Optional) The query (q) parameter filters the results to only those that include that search term. The q parameter supports AND, OR, and NOT operators.",
      "examples": [
          "climate change AND NOT weather"
      ]
  },
  "tag": {
      "title": "Tag",
      "type": "string",
      "description": "(Optional) A tag is a piece of data that is used by The Guardian to categorize content. Use this parameter to filter results by showing only the ones matching the entered tag. See the API documentation for more details.",
      "examples": [
          "environment/recycling"
      ]
  },
  "section": {
      "title": "Section",
      "type": "string",
      "description": "(Optional) Use this to filter results by a particular section. See the API documentation for more details.",
      "examples": [
          "technology"
      ]
  },
  "end_date": {
      "title": "End Date",
      "type": "string",
      "description": "(Optional) Use this to set the maximum date (YYYY-MM-DD) of the results. Results newer than the end_date will not be shown. By default, the current date (today) is set for incremental syncs. See the API documentation for more details.",
      "pattern": "^([1-9][0-9]{3})\\-(0?[1-9]|1[012])\\-(0?[1-9]|[12][0-9]|3[01])$",
      "examples": [
          "YYYY-MM-DD"
      ]
  }
}
```

## Supported sync modes

The Guardian API source connector supports the following [sync modes](https://docs.airbyte.io/integrations/sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Performance considerations

The API key that you are assigned is rate-limited. As such, any applications that depend on making a large number of requests on a polling basis are likely to exceed their daily quota and be prevented from making further requests until the next period begins.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                        |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18654](https://github.com/airbytehq/airbyte/pull/18654) | 🎉 New Source: The Guardian API [low-code CDK] |