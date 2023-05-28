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

## Setup Guide

### Obtaining API Key

In order to set up the the-guardian-api source connector, you will need to obtain an API key from the Guardian API website. To get an API key, follow these steps:

1. Visit the [The Guardian Open Platform website](https://open-platform.theguardian.com/).
2. Click on the "Get Started" button.
3. Fill out the registration form and click "Register" to create an account.
4. Once your account is created, log in and click on the "API Console" button.
5. In the API Console, click on the "Register new API key" button.
6. Fill out the form with a name and description for your API key, then click "Register".
7. After registration, you will be provided with an API Key which can be used to configure the the-guardian-api source connector.

### Configuring the Connector

With your API Key in hand, you can proceed to configure the the-guardian-api source connector in Airbyte. The following options are available for configuration:

- **API Key**: Enter the API Key obtained in the previous step. The key is case sensitive.

- **Start Date**: Enter the minimum date (YYYY-MM-DD) of the results. Results older than the start_date will not be shown.

- **Query** (Optional): Enter a search term to filter the results to only those that include that term. The 'q' parameter supports AND, OR, and NOT operators. Examples:
  - `environment AND NOT water`
  - `environment AND political`
  - `amusement park`
  - `political`

- **Tag** (Optional): Enter a tag to filter results by showing only the ones matching the entered tag. You can find a list of all tags [here](https://content.guardianapis.com/tags?api-key=test) and the tags endpoint documentation [here](https://open-platform.theguardian.com/documentation/tag). Examples:
  - `environment/recycling`
  - `environment/plasticbags`
  - `environment/energyefficiency`

- **Section** (Optional): Enter a section to filter the results by a particular section. You can find a list of all sections [here](https://content.guardianapis.com/sections?api-key=test) and the sections endpoint documentation [here](https://open-platform.theguardian.com/documentation/section). Examples:
  - `media`
  - `technology`
  - `housing-network`

- **End Date** (Optional): Enter the maximum date (YYYY-MM-DD) of the results. Results newer than the end_date will not be shown. Default is set to the current date (today) for incremental syncs.

Once you have completed your configuration, click "Save" to start using the the-guardian-api source connector with Airbyte.

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

| Version | Date       | Pull Request                                              | Subject                                        |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18654](https://github.com/airbytehq/airbyte/pull/18654) | 🎉 New Source: The Guardian API [low-code CDK] |
