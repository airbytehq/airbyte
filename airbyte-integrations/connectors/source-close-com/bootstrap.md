# Close.com

**Close.com** is a web based CRM for sales teams.
The Close.com API allows users to retrieve information about leads, contacts, activities etc.
**API** doc available [here](https://developer.close.com/).

Auth uses a pre-created API token which can be created in the UI. 
`skip_` and `limit_` params are used for pagination. 
Rate limiting is just a standard exponential backoff when you see a 429 HTTP status code. Close.com puts the retry time in the `rate_reset` response body. Rate-reset is the same as retry-after.

Some of streams supports Incremental sync. Incremental sync available when API endpoint supports one of query params: `date_created` or `date_updated`.

Also, Close.com source has Mixin streams for *activities*, *tasks*, *custom fields*, *connected accounts*, and *bulk actions*. 
It is implemented due to different schema for each of mixin type stream.
