# The Guardian API

## Overview

The Guardian API source can sync data from [The Guardian](https://open-platform.theguardian.com/) website.

## Prerequisites

To set up the Guardian API connector, you will need to generate an API key. This API key is necessary to gain access to the website's data. You can obtain the API key by following the steps listed below:

1. Go to [The Guardian Open Platform](https://open-platform.theguardian.com/access/) page. 
2. Fill out the required fields and submit the form.
3. Once you submit the form, you will receive an email from The Guardian team with the API key. 

## Configuration 

### For Airbyte Cloud:

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, select **The Guardian API** from the Source type dropdown list.
4. Enter your API key as the mandatory parameter.
5. You may enter the following (optional) parameters for more granular data retrieval:
- `q` (query) - to filter the data to only those that include specific search terms.
- `tag` - to filter results by showing only the ones matching the entered tag. 
- `section` - to filter the results by a particular section.
- `end_date` - to set the maximum date of the results. Results newer than the end_date will not be shown. 

6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Click on **Create a new connection** from the top of the page.
3. In the sidebar, select **Add Source**.
4. Select **The Guardian API** from the list of sources.
5. Enter your API Key as the mandatory parameter.
6. You may enter the following (optional) parameters for more granular data retrieval:
- `q` (query) - to filter the data to only those that include specific search terms.
- `tag` - to filter results by showing only the ones matching the entered tag.
- `section` - to filter the results by a particular section.
- `end_date` - to set the maximum date of the results. Results newer than the end_date will not be shown. 

7. Click **Test Connection** to verify your details are correct.
8. Once verified, click **Create**.

## Supported sync modes

The Guardian API source connector supports Full Refresh Sync only.

## Output schema

The Guardian API source connector syncs data items with the following fields:

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
Each data item is a news article, and the fields are self-explanatory.

## Performance considerations

The Guardian API implements a daily quota for making requests to the website. Please ensure that your application does not exceed the allocated request limit. 

## Additional Resources

Here is the source configuration JSON schema:

```
documentationUrl: https://docs.airbyte.io/integrations/sources/the-guardian-api
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: The Guardian Api Spec
  type: object
  required:
    - api_key
    - start_date
  additionalProperties: true
  properties:
    api_key:
      title: API Key
      type: string
      description: Your API Key. See here: https://open-platform.theguardian.com/access/. The key is case sensitive.
      airbyte_secret: true
    start_date:
      title: Start Date
      type: string
      description: Use this to set the minimum date (YYYY-MM-DD) of the results. Results older than the start_date will not be shown.
      pattern: ^([1-9][0-9]{3})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$
      examples:
        - YYYY-MM-DD
    query:
      title: Query
      type: string
      description: (Optional) The query (q) parameter filters the results to only those that include that search term. The q parameter supports AND, OR and NOT operators.
      examples:
        - environment AND NOT water
        - environment AND political
        - amusement park
        - political
    tag:
      title: Tag
      type: string
      description: (Optional) A tag is a piece of data that is used by The Guardian to categorise content. Use this parameter to filter results by showing only the ones matching the entered tag. See here: https://content.guardianapis.com/tags?api-key=test for a list of all tags, and here: https://open-platform.theguardian.com/documentation/tag for the tags endpoint documentation.
      examples:
        - environment/recycling
        - environment/plasticbags
        - environment/energyefficiency
    section:
      title: Section
      type: string
      description: (Optional) Use this to filter the results by a particular section. See here: https://content.guardianapis.com/sections?api-key=test for a list of all sections, and here: https://open-platform.theguardian.com/documentation/section for the sections endpoint documentation.
      examples:
        - media
        - technology
        - housing-network
    end_date:
      title: End Date
      type: string
      description: (Optional) Use this to set the maximum date (YYYY-MM-DD) of the results. Results newer than the end_date will not be shown. Default is set to the current date (today) for incremental syncs.
      pattern: ^([1-9][0-9]{3})\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$
      examples:
        - YYYY-MM-DD
```

For more information, please see The Guardian's API documentation [here](https://open-platform.theguardian.com/documentation/search).