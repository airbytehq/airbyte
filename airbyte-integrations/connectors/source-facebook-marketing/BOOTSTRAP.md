# Facebook Marketing

The Facebook Marketing API allows a developer to retrieve information about a user’s marketing endeavors on the Facebook platform. Some example use cases:
- Retrieve the performance of the ad campaigns in the user’s account
- Retrieve all ad campaigns that a user has run in the past

There are roughly two kinds of queries we’d be interested in making to Facebook Marketing API:
1. Obtain attributes about entities in the API e.g: what campaigns did we run, what ads, etc…
2. Obtain statistics about ad campaigns e.g: how many people saw them, how many people bought products as a result, etc... This is the most common use case for the API, known as [insights](https://developers.facebook.com/docs/marketing-api/insights).

In general when querying the FB API for insights there are a few things to keep in mind:
- You can input [parameters](https://developers.facebook.com/docs/marketing-api/insights/parameters) to control which response you get e.g: you can get statistics at the level of an ad, ad group, campaign, or ad account
- An important parameter you can configure is [fields](https://developers.facebook.com/docs/marketing-api/insights/fields), which controls which information is included in the response. For example, if you include “campaign.title” as a field, you will receive the title of that campaign in the response. When fields is not specified, many endpoints return a minimal set of fields.
- Data can be segmented using [breakdowns](https://developers.facebook.com/docs/marketing-api/insights/breakdowns) i.e: you can either get the number of impressions for a campaign as a single number or you can get it broken down by device, gender, or country of the person viewing the advertisement. Make sure to read the provided link about breakdowns in its entirety to understand 

Also make sure to read [this overview of insights](https://developers.facebook.com/docs/marketing-api/insights) in its entirety to have a strong understanding of this important aspect of the API. 

See [this](https://docs.airbyte.io/integrations/sources/facebook-marketing) link for the nuances about the connector.
