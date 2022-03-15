# Chartmogul
Chartmogul is an online subscription analytics platform. It retrieves data from payment processors (e.g. Stripe) and makes sense out of it.

## Streams

Connector currently implements following full refresh streams:
* [Customers](https://dev.chartmogul.com/reference/list-customers)
* [CustomerCount] (https://dev.chartmogul.com/reference/retrieve-customer-count)
* [Activities](https://dev.chartmogul.com/reference/list-activities)

`start_date` config is used for retrieving `Activies`. `Customers` stream does not use this config. Even if it was possible to filter by `start_date`, it would cause issues when modeling data. That is because activies after `start_date` can be triggered by customers who were created way before that.

### Incremental streams
Incremental streams were not implemented due to following reasons:
* `Customers` API endpoint does not provide filtering by creation/update date.
* `Activities` API does provide pagination based on last entries UUID, however it is not stable, since it is possible to for activity to disappear retrospectively.

### Next steps
It is theoretically possible to make `Activities` stream incremental. One would need to keep track of both UUID and created_at and read stream until `datetime.now()`. Dynamic end date would be necessary since activities can also have a future date. Since data can be changed retrospectively, a `lookback window` would also be necessary to catch all the changes.

### Rate limits
The API rate limit is at 40 requests/second. Read [Rate Limits](https://dev.chartmogul.com/docs/rate-limits) for more informations.