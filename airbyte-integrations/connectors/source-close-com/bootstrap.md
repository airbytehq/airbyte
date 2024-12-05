# Close.com

**Close.com** is a web based CRM for sales teams.
The Close.com API allows users to retrieve information about leads, contacts, activities etc.
**API** doc available [here](https://developer.close.com/).

Auth uses a pre-created API token which can be created in the UI.

In one case, `_skip` and `_limit` params are used for pagination.
Some streams have `_limit` param (`number_of_items_per_page` variable in code) due to maximum Close.com limit of data per request.
In other case, the `cursor_next` field from response is used for pagination in `_cursor` param.

Rate limiting is just a standard exponential backoff when you see a 429 HTTP status code. Close.com puts the retry time in the `rate_reset` response body. Rate-reset is the same as retry-after.

Some of streams supports Incremental sync. Incremental sync available when API endpoint supports one of query params: `date_created` or `date_updated`.

There are not `state_checkpoint_interval` for _activities_ and _events_ due to impossibility ordering data ascending.

Also, Close.com source has general stream classes for _activities_, _tasks_, _custom fields_, _connected accounts_, and _bulk actions_.
It is implemented due to different schema for each of stream.

See [this](https://docs.airbyte.io/integrations/sources/close-com) link for the nuances about the connector.
