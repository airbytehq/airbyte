# Google Search Console

From [the docs](https://support.google.com/webmasters/answer/9128668?hl=en):

Google Search Console is a free service offered by Google that helps you monitor, maintain, and troubleshoot your site's presence in Google Search results.

Search Console offers tools and reports for the following actions:

- Confirm that Google can find and crawl your site.
- Fix indexing problems and request re-indexing of new or updated content.
- View Google Search traffic data for your site: how often your site appears in Google Search, which search queries show your site, how often searchers click through for those queries, and more.
- Receive alerts when Google encounters indexing, spam, or other issues on your site.
- Show you which sites link to your website.
- Troubleshoot issues for AMP, mobile usability, and other Search features.

The API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/parameters.

## Endpoints and Streams:

1. [Site](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites) – Full refresh
2. [Sitemaps](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps) – Full refresh
3. [Analytics](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics) – Full refresh, Incremental

There are multiple streams in the `Analytics` endpoint.
We have them because if we want to get all the data from the GSC (using the SearchAnalyticsAllFields stream),
we have to deal with a large dataset.

In order to reduce the amount of data, and to retrieve a specific dataset (for example, to get country specific data)
we can use SearchAnalyticsByCountry.
So each of the SearchAnalytics streams groups data by certain dimensions like date, country, page, etc.

There are:

1.  SearchAnalyticsByDate
2.  SearchAnalyticsByCountry
3.  SearchAnalyticsByPage
4.  SearchAnalyticsByQuery
5.  SearchAnalyticsAllFields

## Authorization

There are 2 types of authorization `User Account` and `Service Account`.
To chose one we use an authorization field with the `oneOf` parameter in the `spec.json` file.

See the links below for information about specific streams and some nuances about the connector:

- [information about streams](https://docs.google.com/spreadsheets/d/1s-MAwI5d3eBlBOD8II_sZM7pw5FmZtAJsx1KJjVRFNU/edit#gid=1796337932) (`Google Search Console` tab)
- [nuances about the connector](https://docs.airbyte.io/integrations/sources/google-search-console)
