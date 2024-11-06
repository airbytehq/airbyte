# Google Ads

Link to API Docs is [here](https://developers.google.com/google-ads/api/docs/start).

The GAds API is basically a SQL interface on top of the Google Ads API resources. The reference for the SQL language (called GAQL) can be found [here](https://developers.google.com/google-ads/api/docs/query/overview).

The resources are listed [here](https://developers.google.com/google-ads/api/reference/rpc/v8/overview).

When querying data, there are three categories of information that can be fetched:

- **Attributes**: These are properties of the various entities in the API e.g: the title or ID of an ad campaign.
- **Metrics**: metrics are statistics related to entities in the API. For example, the number of impressions for an ad or an ad campaign. All available metrics can be found [here](https://developers.google.com/google-ads/api/fields/v17/metrics).
- **Segments**: These are ways to partition metrics returned in the query by particular attributes. For example, one could query for the number of impressions (views of an ad) by running SELECT
  metrics.impressions FROM campaigns which would return the number of impressions for each campaign e.g: 10k impressions. Or you could query for impressions segmented by device type e.g; SELECT
  metrics.impressions, segments.device FROM campaigns which would return the number of impressions broken down by device type e.g: 3k iOS and 7k Android. When summing the result across all segments,
  the sum should be the same (approximately) as when requesting the whole query without segments. This is a useful feature for granular data analysis as an advertiser may for example want to know if
  their ad is successful with a particular kind of person over the other. See more about segmentation [here](https://developers.google.com/google-ads/api/docs/concepts/retrieving-objects).

If you want to get a representation of the raw resources in the API e.g: just know what are all the ads or campaigns in your Google account, you would query only for attributes e.g. SELECT campaign.title FROM campaigns.

But if you wanted to get reports about the data (a common use case is impression data for an ad campaign) then you would query for metrics, potentially with segmentation.

See the links below for information about specific streams and some nuances about the connector:

- [information about streams](https://docs.google.com/spreadsheets/d/1s-MAwI5d3eBlBOD8II_sZM7pw5FmZtAJsx1KJjVRFNU/edit#gid=1796337932) (`Google Ads` tab)
- [nuances about the connector](https://docs.airbyte.io/integrations/sources/google-ads)
