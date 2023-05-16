# The Guardian API

## Overview

The Guardian API source can sync data from the [The Guardian](https://open-platform.theguardian.com/)

## Requirements

To access the API, you will need to sign up for an API key, which should be sent with every request. 

### Get an API Key 

1. Visit [The Guardian's Developer Open Platform](https://open-platform.theguardian.com/access)
2. Click on the "Get an API key" button at the bottom of the page.
3. Fill in the required fields and click "Submit".

## Optional parameters 

The following optional parameters can be provided to the connector: 

##### `q` (query)

The `q` (query) parameter filters the results to only those that include that search term. The `q` parameter supports `AND`, `OR` and `NOT` operators. For example, if you're looking for political content published in 2014, use the URL: 
```https://content.guardianapis.com/search?q=debate&tag=politics/politics&from-date=2014-01-01&api-key=test```

##### `tag`

A tag is a piece of data that is used to categorise content. All Guardian content is manually categorised using these tags, of which there are more than 50,000. Use this parameter to filter results by showing only the ones matching the entered tag. 
* **List of all tags:** <a href="https://content.guardianapis.com/tags?api-key=test">The Guardian Tags</a>
* **Tag Endpoint Documentation:** <a href="https://open-platform.theguardian.com/documentation/tag">Tags Endpoint Documentation</a>


##### `section`

Use this to filter the results by a particular section. 
* **List of all sections:** <a href="https://content.guardianapis.com/sections?api-key=test">The Guardian Sections</a>
* **Section Endpoint Documentation:** <a href="https://open-platform.theguardian.com/documentation/section">Sections Endpoint Documentation</a>

##### `order-by`

Use this to sort the results. The three available sorting options are - newest, oldest, relevance. For enabling incremental syncs set order-by to oldest.

##### `start_date`

Use this to set the minimum date (YYYY-MM-DD) of the results. Results older than the start_date will not be shown.

##### `end_date`

Use this to set the maximum date (YYYY-MM-DD) of the results. Results newer than the end_date will not be shown. Default is set to the current date (today) for incremental syncs.

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

Follow the steps below to set up The Guardian API connector in Airbyte.

## Step 1: Create a new connection 

1. Launch the Airbyte application and navigate to the Connections tab from the left-hand menu.
2. Click on the "Create New Connection" button.
3. Choose "The Guardian API" from the dropdown.
4. Enter your API key in the required field.

## Step 2: Set optional parameters 

The following optional parameters are available to configure: 

- **Query:** Filter results by content that includes a particular search term.
- **Tag:** Filter results by a specific tag from the list of The Guardian tags. 
- **Section:** Filter results by a specific section from the list of The Guardian sections.
- **Order By:** Sort results by newest, oldest, or relevance.
- **Start Date:** Set the minimum date of the results.
- **End Date:** Set the maximum date of the results.

## Supported sync modes

The Guardian API source connector supports the following [sync modes](https://docs.airbyte.io/integrations/sources/the-guardian-api):

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