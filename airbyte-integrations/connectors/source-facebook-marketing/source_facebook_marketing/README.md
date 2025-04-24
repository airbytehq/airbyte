# Structure

- api.py - everything related to FB API, error handling, throttle, call rate
- source.py - mainly check and discovery logic
- spec.py - connector's specification
- streams/ - everything related to streams, usually it is a module, but we have too much for one file

  - base_streams.py - all general logic should go there, you define class of streams as general as possible
  - streams.py - concrete classes, one for each stream, here should be only declarative logic and small overrides
  - base_insights_streams.py - piece of general logic for big subclass of streams - insight streams

  - async_job.py - logic about asynchronous jobs
  - async_job_manager.py - you will find everything about managing groups of async job here
  - common.py - some utils

# FB findings

## API

FB Marketing API provides three ways to interact:

- single request
- batch request
- async request

FB provides a `facebook_business` library, which is an auto generated code from their API spec.
We use it because it provides:

- nice error handling
- batch requests helpers
- auto serialize/de-serialize responses to FB objects
- transparently iterates over paginated response

## Single request

Is the most common way to request something.
We use the two-steps strategy to read most of the data:

1. first request to get list of IDs (filtered by cursor if supported)
2. loop over list of ids and request details for each ID, this step sometimes use batch request

## Batch request

is a batch of requests serialized in the body of a single request.
The response of such request will be a list of responses for each individual request (body, headers, etc).
FB lib use interface with callbacks, batch object will call corresponding (success or failure) callback for each type of response.
FB lib also catch fatal errors from the API (500, …) and instead of calling `on_failure` callback will return a new batch object with list of failed requests.
FB API limit number of requests in a single batch to 50.

**Important note**:

    Batch object doesn’t perform pagination of individual responses,
    so you may lose data if the response have pagination.

## Async Request

FB recommends to use Async Requests when common requests begin to timeout.
Async Request is a 3-step process:

- create async request
- check its status (in a loop)
- fetch response when status is done

### Combination with batch

Unfortunately all attempts to create multiple async requests in a single batch failed - `ObjectParser` from FB lib don’t know how to parse `AdReportRun` response.
Instead, we use batch to check status of multiple async jobs at once (respecting batch limit of 50)

### Insights

We use Async Requests to read Insights, FB API for this called `AdReportRun`.
Insights are reports based on ads performance, you can think about it as an SQL query:

```sql
select <fields> from <edge_object> where <filter> group by <level>, <breakdowns>;
```

Our insights by default look like this:

```sql
select <all possible fields> from AdAccount(me) where start_date = …. and end_date = …. group by ad, <breakdown>
```

FB will perform calculations on its backed with various complexity depending on fields we ask, most heavy fields are unique metrics: `unique_clicks`, `unique_actions`, etc.

Additionally, Insights has fields that show stats from last N days, so-called attribution window, it can be `1d`, `7d`, and `28d`, by default we use all of them.
According to FB docs insights data can be changed up to 28 days after it has being published.
That's why we re-read 28 days in the past from now each time we sync insight stream.

When amount of data and computation is too big for FB servers to handle the jobs start to failing. Throttle and call rate metrics don’t reflect this problem and can’t be used to monitor.
Instead, we use the following technic.
Taking into account that we group by ad we can safely change our from table to smaller dataset/edge_object (campaign, adset, ad).
Empirically we figured out that account level insights contains data for all campaigns from last 28 days and, very rarely, campaigns that didn’t even start yet.
To solve this mismatch, at least partially, we get list of campaigns for last 28 days from the insight start date.
The current algorithm looks like this:

```
create async job for account level insight for the day A
	if async job failed:
		restart it
	if async job failed again:
		get list of campaigns for last 28 day
		create async job for each campaign and day A
```

If campaign-level async job fails second time we split it by `AdSets` or `Ads`.

Reports from users show that sometimes async job can stuck for very long time (hours+),
and because FB doesn’t provide any canceling API after 1 hour of waiting we start another job.
