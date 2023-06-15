# Incremental sync

An incremental sync is a sync which pulls only the data that has changed since the previous sync (as opposed to all the data available in the data source).

This is especially important if there are a large number of records to sync and/or the API has tight request limits which makes a full sync of all records on a regular schedule too expensive or too slow.

Incremental syncs are usually implemented using a cursor value (like a timestamp) that delineates which data was pulled and which data is new. A very common cursor value is an `updated_at` timestamp. This cursor means that records whose `updated_at` value is less than or equal than that cursor value have been synced already, and that the next sync should only export records whose `updated_at` value is greater than the cursor value.

To use incremental syncs, the API endpoint needs to fullfil the following requirements:
* Records contain a top-level date/time field that defines when this record was last updated (the "cursor field")
  * If the record's cursor field is nested, you can use an "Add Field" transformation to copy it to the top-level, and a Remove Field to remove it from the object. This will effectively move the field to the top-level of the record
* It's possible to filter/request records by the cursor field
* The records are sorted in ascending order based on their cursor field

The knowledge of a cursor value also allows the Airbyte system to automatically keep a history of changes to records in the destination. To learn more about how different modes of incremental syncs, check out the [Incremental Sync - Append](/understanding-airbyte/connections/incremental-append/) and [Incremental Sync - Deduped History](/understanding-airbyte/connections/incremental-deduped-history) pages.

## Configuration

To configure incremental syncs for a stream in the connector builder, you have to specify how the records will represent the **"last changed" / "updated at" timestamp**, the **initial time range** to fetch records for and **how to request records from a certain time range**.

In the builder UI, these things are specified like this:
* The "Cursor field" is the property in the record that defines the date and time when the record got changed. It's used to decide which records are synced already and which records are "new"
* The "Datetime format" specifies the format the cursor field is using to specify date and time. Check out the [YAML reference](/connector-development/config-based/understanding-the-yaml-file/reference#/definitions/DatetimeBasedCursor) for a full list of supported formats.
* The "Cursor granularity" is the smallest time unit supported by the API to specify the time range to request records for expressed as [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations)
* The "Start datetime" is the initial start date of the time range to fetch records for. When doing incremental syncs, the second sync will overwrite this date with the last record that got synced so far.
* The "End datetime" is the end date of the time range to fetch records for. In most cases it's set to the current date and time when the sync is started to sync all changes that happened so far.
* The "Inject start/end time into outgoing HTTP request" defines how to request records that got changed in the time range to sync. In most cases the start and end time is added as a request parameter or body parameter

## Example

The [API of The Guardian](https://open-platform.theguardian.com/documentation/search) has a `/search` endpoint that allows to extract a list of articles.

The `/search` endpoint has a `from-date` and a `to-date` query parameter which can be used to only request data for a certain time range.

Content records have the following form:
```
{
    "id": "world/2022/oct/21/russia-ukraine-war-latest-what-we-know-on-day-240-of-the-invasion",
    "type": "article",
    "sectionId": "world",
    "sectionName": "World news",
    "webPublicationDate": "2022-10-21T14:06:14Z",
    "webTitle": "Russia-Ukraine war latest: what we know on day 240 of the invasion",
    // ...
}
```

As this fulfills the requirements for incremental syncs, we can configure the "Incremental sync" section in the following way:
* "Cursor field" is set to `webPublicationDate`
* "Datetime format" is set to `%Y-%m-%dT%H:%M:%SZ`
* "Start datetime" is set to "user input" to allow the user of the connector configuring a Source to specify the time to start syncing
* "End datetime" is set to "now" to fetch all articles up to the current date
* "Inject start time into outgoing HTTP request" is set to `request_parameter` with "Field" set to `from-date`
* "Inject end time into outgoing HTTP request" is set to `request_parameter` with "Field" set to `to-date`

<iframe width="640" height="835" src="https://www.loom.com/embed/78eb5da26e2e4f4aa9c3a48573d9ed3b" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

This API orders records by default from new to old, which is not optimal for a reliable sync as the last encountered cursor value will be the most recent date even if some older records did not get synced (for example if a sync fails halfway through). It's better to start with the oldest records and work your way up to make sure that all older records are synced already once a certain date is encountered on a record. In this case the API can be configured to behave like this by setting an additional parameter:
* At the bottom of the stream configuration page, add a new "Request parameter"
* Set the key to `order-by`
* Set the value to `oldest`

Setting the start date in the "Testing values" to a date in the past like **2023-04-09T00:00:00Z** results in the following request:
<pre>
curl 'https://content.guardianapis.com/search?order-by=oldest&from-date=<b>2023-04-09T00:00:00Z</b>&to-date={`now`}'
</pre>

The last encountered date will be saved as part of the connection - when the next sync is running, it picks up from the last record. Let's assume the last ecountered article looked like this:
<pre>
{`{
  "id": "business/live/2023/apr/15/uk-bosses-more-optimistic-energy-prices-fall-ai-spending-boom-economics-business-live",
  "type": "liveblog",
  "sectionId": "business",
  "sectionName": "Business",
  "webPublicationDate": `}<b>"2023-04-15T07:30:58Z"</b>{`,
}`}
</pre>

Then when a sync is triggered for the same connection the next day, the following request is made:
<pre>
curl 'https://content.guardianapis.com/search?order-by=oldest&from-date=<b>2023-04-15T07:30:58Z</b>&to-date={`<now>`}'
</pre>

The `from-date` is set to the cutoff date of articles synced already and the `to-date` is set to the current date.

:::info
In some cases, it's helpful to reference the start and end date of the interval that's currently synced, for example if it needs to be injected into the URL path of the current stream. In these cases it can be referenced using the `{{ stream_interval.start_date }}` and `{{ stream_interval.end_date }}` [placeholders](/connector-development/config-based/understanding-the-yaml-file/reference#variables). Check out [the tutorial](./tutorial.mdx#adding-incremental-reads) for such a case.
:::

## Advanced settings

The description above is sufficient for a lot of APIs. However there are some more subtle configurations which sometimes become relevant. 

### Split up interval

When incremental syncs are enabled and "Split up interval" is set, the connector is not fetching all records since the cutoff date at once - instead it's splitting up the time range between the cutoff date and the desired end date into intervals based on the "Step" configuration expressed as [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations).

The "cursor granularity" also needs to be set to an ISO 8601 duration - it represents the smallest possible time unit the API supports to filter records by. It's used to ensure the start of a interval does not overlap with the end of the previous one.

For example if the "Step" is set to 10 days (`P10D`) and the "Cursor granularity" set to second (`PT1S`) for the Guardian articles stream described above and a longer time range, then the following requests will be performed:
<pre>
curl 'https://content.guardianapis.com/search?order-by=oldest&from-date=<b>2023-01-01T00:00:00Z</b>&to-date=<b>2023-01-10T00:00:00Z</b>'{`\n`}
curl 'https://content.guardianapis.com/search?order-by=oldest&from-date=<b>2023-01-10T00:00:00Z</b>&to-date=<b>2023-01-20T00:00:00Z</b>'{`\n`}
curl 'https://content.guardianapis.com/search?order-by=oldest&from-date=<b>2023-01-20T00:00:00Z</b>&to-date=<b>2023-01-30T00:00:00Z</b>'{`\n`}
...
</pre>

After an interval is processed, the cursor value of the last record will be saved as part of the connection as the new cutoff date.

If left unset, the connector will not split up the time range at all but will instead just request all records for the entire target time range. This configuration works for all connectors, but there are two reasons to change it:
* **To protect a connection against intermittent failures** - if the "Step" size is a day, the cutoff date is saved after all records associated with a day are proccessed. If a sync fails halfway through because the API, the Airbyte system, the destination or the network between these components has a failure, then at most one day worth of data needs to be resynced. However, a smaller step size might cause more requests to the API and more load on the system. It depends on the expected amount of data and load characteristics of an API what step size is optimal, but for a lot of applications the default of one month is a good starting point.
* **The API requires the connector to fetch data in pre-specified chunks** - for example the [Exchange Rates API](https://exchangeratesapi.io/documentation/) makes the date to fetch data for part of the URL path and only allows to fetch data for a single day at a time

### Lookback window

The "Lookback window" specifies a duration that is subtracted from the last cutoff date before starting to sync.

Some APIs update records over time but do not allow to filter or search by modification date, only by creation date. For example the API of The Guardian might change the title of an article after it got published, but the `webPublicationDate` still shows the original date the article got published initially.

In these cases, there are two options:
* **Do not use incremental sync** and always sync the full set of records to always have a consistent state, losing the advantages of reduced load and [automatic history keeping in the destination](/understanding-airbyte/connections/incremental-deduped-history)
* **Configure the "Lookback window"** to not only sync exclusively new records, but resync some portion of records before the cutoff date to catch changes that were made to existing records, trading off data consistency and the amount of synced records. In the case of the API of The Guardian, news articles tend to only be updated for a few days after the initial release date, so this strategy should be able to catch most updates without having to resync all articles.

Reiterating the example from above with a "Lookback window" of 2 days configured, let's assume the last encountered article looked like this:
<pre>
{`{
  "id": "business/live/2023/apr/15/uk-bosses-more-optimistic-energy-prices-fall-ai-spending-boom-economics-business-live",
  "type": "liveblog",
  "sectionId": "business",
  "sectionName": "Business",
  "webPublicationDate": `}<b>{`"2023-04-15T07:30:58Z"`}</b>{`,
}`}
</pre>

Then when a sync is triggered for the same connection the next day, the following request is made:
<pre>
curl 'https://content.guardianapis.com/search?order-by=oldest&from-date=<b>2023-04-13T07:30:58Z</b>&to-date={`<now>`}'
</pre>

## Custom parameter injection

Using the "Inject start time / end time into outgoing HTTP request" option in the incremental sync form works for most cases, but sometimes the API has special requirements that can't be handled this way:
* The API requires adding a prefix or a suffix to the actual value
* Multiple values need to be put together in a single parameter
* The value needs to be injected into the URL path
* Some conditional logic needs to be applied

To handle these cases, disable injection in the incremental sync form and use the generic parameter section at the bottom of the stream configuration form to freely configure query parameters, headers and properties of the JSON body, by using jinja expressions and [available variables](/connector-development/config-based/understanding-the-yaml-file/reference/#/variables). You can also use these variables as part of the URL path.

For example the [Sendgrid API](https://docs.sendgrid.com/api-reference/e-mail-activity/filter-all-messages) requires setting both start and end time in a `query` parameter.
For this case, you can use the `stream_interval` variable to configure a request parameter with "key" `query` and "value" `last_event_time BETWEEN TIMESTAMP "{{stream_interval.start_time}}" AND TIMESTAMP "{{stream_interval.end_time}}"` to filter down to the right window in time.