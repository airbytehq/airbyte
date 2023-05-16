# The Guardian API

## Overview

The Guardian API source can sync data from [The Guardian Open Platform API](https://open-platform.theguardian.com/).

## Requirements

Before you set up the The Guardian API connector in Airbyte, you need to sign up for an API key. You can register for an API key [here](https://open-platform.theguardian.com/access/).

The following (optional) parameters can be provided: 

- `q` (query): Filters the results to only those that include that search term. Supports AND, OR, and NOT operators.
- `tag`: Use a tag to categorize and filter the results. See [here](https://content.guardianapis.com/tags?api-key=test) for a list of all available tags.
- `section`: Filter the results by a particular section. See [here](https://content.guardianapis.com/sections?api-key=test) for a list of all sections.
- `order-by`: Sort the results. Available sorting options include newest, oldest, and relevance. Set order-by to oldest to enable incremental syncs.
- `start_date`: Set the minimum date (YYYY-MM-DD) of the results. Results older than the start_date will not be shown.
- `end_date`: Set the maximum date (YYYY-MM-DD) of the results. Results newer than the end_date will not be shown. For incremental syncs, the default is set to the current date (today).

## Output schema

Each content item (news article) has the following structure:

```yaml
{
    "id": "string",
    "type": "string",
    "sectionId": "string",
    "sectionName": "string",
    "webPublicationDate": "string",
    "webTitle": "string",
    "webUrl": "string",
    "apiUrl": "string",
    "isHosted": "boolean",
    "pillarId": "string",
    "pillarName": "string"
}
```

The source is capable of syncing the content stream.

## Setup guide

1. Navigate to the **New Source** page in Airbyte.

2. Select "The Guardian API" from the dropdown menu.

3. In the **Setup Connection** page, enter your The Guardian API key. The key is case-sensitive and is mandatory.

   You can find more information about obtaining your API key [here](https://open-platform.theguardian.com/access/).
   
4. Enter any optional parameters as per your requirements. Refer to the `Requirements` section of this document for more information.

5. Click **Test**. If your API key is valid, you should see a successful response.

6. Click **Create** to complete the setup.

## Supported sync modes

The Guardian API source connector supports the following [sync modes](https://docs.airbyte.io/integrations/sources/the-guardian-api):

| Feature | Supported? |
| :------ | :--------- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Namespaces | No |

## Performance considerations

Be mindful that the key you are assigned is rate-limited, and as such, any applications that depend on making large numbers of requests on a polling basis may exceed their daily quota and thus be prevented from making further requests until the next period. You can find more information about rate limits [here](https://open-platform.theguardian.com/documentation/rate-limits).

## Next Steps

Now that you've successfully set up The Guardian API in Airbyte, you can further configure your sync with the destination of your choice. For more information, refer to the [Airbyte Documentation](https://docs.airbyte.io/).