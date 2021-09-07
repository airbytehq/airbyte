# Google Search Console

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

There are:
   1. SearchAnalyticsByDate
   2. SearchAnalyticsByCountry
   3. SearchAnalyticsByPage
   4. SearchAnalyticsByQuery
   5. SearchAnalyticsAllFields

## Authorization

There are 2 types of authorization `User Account` and `Service Account`.
To chose one we use an authorization field with the `oneOf` parameter  in the `spec.json` file.


## Analytics

### 1. Pagination

The `next_page_token` implements pagination functionality. This method gets the response and compares the number of records with the constant `ROW_LIMITS` (maximum value 25000), and if they are equal, this means that we get the end of the` Page`, and we need to go further, for this we simply increase the `startRow` parameter in request body by `ROW_LIMIT` value.


### 2. Loop support

The `stream_slices` implements iterator functionality for `site_urls` and `searchType`. The user can pass many `site_url`, and we have to process all of them, we can also pass the` searchType` parameter in the `request body` to get data using some` searchType` value from [` web`, `news `,` image`, `video`]. It's just a double nested loop with a yield statement.


### 3. Incremental sync

With the existing nested loop implementation, we have to store a `cursor_field` for each `site_url` and `searchType`. This functionality is placed in `get_update_state`.


### 4. Request body (analytics streams)

Here is a description of the parameters and implementations of the request body:
   1. The `startDate` is retrieved from the `_get_start_date`, if` SyncMode = full_refresh` just use `start_date` from configuration, otherwise use `get_update_state`.
   2. The `endDate` is retrieved from the `config.json`.
   3. The `sizes` parameter is used to group the result by some dimension. The following dimensions are available: `date`, `country`, `page`, `device`, `query`.
   4. For the `searchType` check the paragraph 2.
   5. For the `startRow` and `rowLimit` check the paragraph 3.