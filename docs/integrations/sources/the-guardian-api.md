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

This guide will walk you through the configuration process for the the-guardian-api Source connector in Airbyte. To set up the connector, you will need to provide the required information in the configuration form. Below is a step-by-step guide to help you fill in the form correctly.

### Obtain API Key

In order to use the the-guardian-api Source connector, you will need an API Key. If you don't already have one, follow these steps to obtain it:

1. Go to the [Guardian Open Platform website](https://open-platform.theguardian.com/).
2. Click on the "Get an API key" button located in the top right.
3. Fill out the following form to register for a new API key. Be sure to choose the correct API Key type (Developer or Commercial) based on your needs.
4. Once you have filled out the form, click "Submit" to request your API key. You will receive an email with the API key in your inbox after successfully completing the registration.

### Configure the the-guardian-api Source Connector

After obtaining your API Key, provide the necessary information in the configuration form as described below:

1. **API Key**: Enter the API Key obtained in the previous step. This field is case sensitive and should be entered exactly as provided.

2. **Start Date**: Enter the minimum date (YYYY-MM-DD) for the articles you want returned by the API. Any results older than the start date will not be shown.

3. **Query** (Optional): If you wish to filter the results by a specific search term, enter it here. This field supports AND, OR, and NOT operators. For example, you can enter `environment AND NOT water` or `environment AND political`.

4. **Tag** (Optional): The Guardian categorizes content using tags. You can use this field to filter results by a specific tag. You can find a list of all tags [here](https://content.guardianapis.com/tags?api-key=test) and additional documentation on tags [here](https://open-platform.theguardian.com/documentation/tag). Enter the tag you want to filter by, for example, `environment/recycling` or `environment/plasticbags`.

5. **Section** (Optional): You can also filter the results by a particular section. To find a list of all available sections, click [here](https://content.guardianapis.com/sections?api-key=test). Additional documentation on sections can be found [here](https://open-platform.theguardian.com/documentation/section). Enter the section you want to filter by, for example, `media` or `technology`.

6. **End Date** (Optional): Enter the maximum date (YYYY-MM-DD) for the articles you want returned by the API. Any results newer than the end date will not be shown. The default value for incremental syncs is the current date (today).

After providing the necessary information, you can use the the-guardian-api Source connector to fetch data from the Guardian API in your Airbyte environment.

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
