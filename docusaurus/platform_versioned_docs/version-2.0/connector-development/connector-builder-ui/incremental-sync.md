# Incremental sync

An incremental sync is a sync which pulls only the data that has changed since the previous sync (as opposed to all the data available in the data source).

This is especially important if there are a large number of records to sync and/or the API has tight request limits which makes a full sync of all records on a regular schedule too expensive or too slow.

Incremental syncs are usually implemented using a cursor value (like a timestamp) that delineates which data was pulled and which data is new. A very common cursor value is an `updated_at` timestamp. This cursor means that records whose `updated_at` value is less than or equal than that cursor value have been synced already, and that the next sync should only export records whose `updated_at` value is greater than the cursor value.

To use incremental syncs, the API endpoint needs to fulfill the following requirements:

- Records contain a top-level date/time field that defines when this record was last updated (the "cursor field")
  - If the record's cursor field is nested, you can use an "Add Field" transformation to copy it to the top-level, and a Remove Field to remove it from the object. This will effectively move the field to the top-level of the record
- It's possible to filter/request records by the cursor field

The knowledge of a cursor value also allows the Airbyte system to automatically keep a history of changes to records in the destination. To learn more about how different modes of incremental syncs, check out the [Incremental Sync - Append](/platform/using-airbyte/core-concepts/sync-modes/incremental-append/) and [Incremental Sync - Append + Deduped](/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) pages.

## Configuration

To configure incremental syncs for a stream in the connector builder, you need to specify the **cursor field**, **datetime formats**, **time filtering capabilities**, and **request injection** settings.

In the builder UI, these are configured as follows:

- **Cursor field** - The property in the record that defines when the record was last updated. This field is used to determine which records have been synced and which are new.
- **Cursor datetime formats** - The possible formats for the cursor field, in order of preference. The first format that matches the cursor field value will be used to parse it. The UI can auto-detect common formats from your test data.
- **Start datetime** - The initial start date for the time range to fetch records. For incremental syncs, subsequent syncs will use the last cursor value as the new start date.
- **End datetime** - The end date for the time range (only available for Range mode). Usually set to "now" to sync all changes up to the current time.
- **Inject start/end time into outgoing HTTP request** - Configures how to send the datetime values to the API (as query parameters, headers, or request body).

### Cursor datetime formats

The Connector Builder supports multiple datetime formats for parsing cursor field values. You can specify multiple formats in order of preference - the first format that successfully parses the cursor value will be used.

The UI can automatically detect common datetime formats from your test data. When you test your stream, if a format is detected that isn't in your current list, you'll see a suggestion to add it.

Common formats include:
- `%Y-%m-%dT%H:%M:%S.%f%z` - ISO 8601 with microseconds and timezone
- `%Y-%m-%dT%H:%M:%SZ` - ISO 8601 with seconds
- `%Y-%m-%d` - Date only
- `%s` - Unix timestamp (seconds)
- `%ms` - Unix timestamp (milliseconds)

This is different from the **outgoing datetime format**, which controls how datetime values are formatted when sent to the API in requests.

## Example

The [API of The Guardian](https://open-platform.theguardian.com/documentation/search) has a `/search` endpoint that allows to extract a list of articles.

The `/search` endpoint has a `from-date` and a `to-date` query parameter which can be used to only request data for a certain time range.

Content records have the following form:

```json
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

- "Cursor field" is set to `webPublicationDate`
- "Cursor datetime formats" is set to `%Y-%m-%dT%H:%M:%SZ`
- "Start datetime" is set to "Interpolated Value" and pointed at `{{ config['start_time'] }}` to allow the user of the connector configuring a Source to specify the time to start syncing
- "End datetime" is set to `{{ now_utc().strftime('%Y-%m-%dT%H:%M:%SZ') }}` to fetch all articles up to the current date
- "Inject start time into outgoing HTTP request" is set to `request_parameter` with "Field" set to `from-date`
- "Inject end time into outgoing HTTP request" is set to `request_parameter` with "Field" set to `to-date`

Setting the start date in the "Testing values" to a date in the past like **2023-04-09T00:00:00Z** results in the following request:

```bash
curl 'https://content.guardianapis.com/search?from-date=<b>2023-04-09T00:00:00Z</b>&to-date={`now`}'
```

The most recent encountered date will be saved as the [*state*](../../understanding-airbyte/airbyte-protocol.md#state--checkpointing) of the connection - when the next sync is running, it picks up from that cutoff date as the new start date. Let's assume the last ecountered article looked like this:

```json
{`{
  "id": "business/live/2023/apr/15/uk-bosses-more-optimistic-energy-prices-fall-ai-spending-boom-economics-business-live",
  "type": "liveblog",
  "sectionId": "business",
  "sectionName": "Business",
  "webPublicationDate": `}<b>"2023-04-15T07:30:58Z"</b>{`,
}`}
```

Then when a sync is triggered for the same connection the next day, the following request is made:

```bash
curl 'https://content.guardianapis.com/search?from-date=<b>2023-04-15T07:30:58Z</b>&to-date={`<now>`}'
```

:::info
If the last record read has a datetime earlier than the end time of the stream interval, the end time of the interval will be stored in the state.
:::

The `from-date` is set to the cutoff date of articles synced already and the `to-date` is set to the current date.

:::info
In some cases, it's helpful to reference the start and end date of the interval that's currently synced, for example if it needs to be injected into the URL path of the current stream. In these cases it can be referenced using the `{{ stream_interval.start_time }}` and `{{ stream_interval.end_time }}` [placeholders](/platform/connector-development/config-based/understanding-the-yaml-file/reference#variables). Check out [the tutorial](./tutorial.mdx#adding-incremental-reads) for such a case.
:::

## Advanced settings

### Outgoing datetime format

The "Outgoing datetime format" specifies how datetime values are formatted when sent to the API in requests. If not specified, the first format from your cursor datetime formats will be used.

Supported format placeholders include:
- `%s` - Unix timestamp (seconds) - `1686218963`
- `%s_as_float` - Unix timestamp as float with microsecond precision - `1686218963.123456`
- `%ms` - Unix timestamp (milliseconds) - `1686218963123`
- `%Y-%m-%dT%H:%M:%S.%f%z` - ISO 8601 with microseconds and timezone
- `%Y-%m-%d` - Date only format
- And many other standard datetime format codes

For a complete list of format codes, see the [Python strftime documentation](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

The description above is sufficient for a lot of APIs. However there are some more subtle configurations which sometimes become relevant.

### Cursor granularity and step sizes

If you don't want to fetch all records since the cutoff date at once, you can split these into intervals using the **Cursor granularity** and **Step** options.

- Step is the range between the cutoff date and the desired end date.

- Cursor granularity represents the smallest possible time unit the API supports, by which you want to filter records. It ensures the start of an interval doesn't overlap with the end of the last one.

Set these values to an [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations).

For example, if the "Step" is set to 10 days (`P10D`) and the "Cursor granularity" set to one second (`PT1S`), using a longer time range for the Guardian articles stream described above results in the following requests.

```bash
curl 'https://content.guardianapis.com/search?from-date=<b>2023-01-01T00:00:00Z</b>&to-date=<b>2023-01-09T23:59:59Z</b>'{`\n`}
curl 'https://content.guardianapis.com/search?from-date=<b>2023-01-10T00:00:00Z</b>&to-date=<b>2023-01-19T23:59:59Z</b>'{`\n`}
curl 'https://content.guardianapis.com/search?from-date=<b>2023-01-20T00:00:00Z</b>&to-date=<b>2023-01-29T23:59:59Z</b>'{`\n`}
...
```

After an interval is processed, the cursor value of the last record will be saved as part of the connection as the new cutoff date, as described in the [example above](#example).

Splitting intervals is useful for two reason.

- **Protecting against sync failures** - If a sync fails, at most one interval's worth of data needs to be resynced

- **API requirements** - Some APIs require data to be fetched in specific time chunks

However, two reasons exist to avoid using these options, as well.

- **Protecting against intermittent failures** - A smaller step size might cause more requests to the API and more load on the system. The optimal interval depends on the expected amount of data and load characteristics of an API.

- **Some API require you fetch data in pre-specified chunks** - The [Exchange Rates API](https://exchangeratesapi.io/documentation/) makes the fetch date part of the URL path. It only allows you to fetch data for a single day at a time.

The correct choice depends entirely on how the API works and the type and volume of data you expect to receive from it. If you find you need to control the interval this way, one month is a good starting point, and you can adjust from there if you need to.

### Lookback window

The "Lookback window" specifies a duration that is subtracted from the last cutoff date before starting to sync.

Some APIs update records over time but do not allow to filter or search by modification date, only by creation date. For example the API of The Guardian might change the title of an article after it got published, but the `webPublicationDate` still shows the original date the article got published initially.

In these cases, there are two options:

- **Do not use incremental sync** and always sync the full set of records to always have a consistent state, losing the advantages of reduced load and [automatic history keeping in the destination](/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)
- **Configure the "Lookback window"** to not only sync exclusively new records, but resync some portion of records before the cutoff date to catch changes that were made to existing records, trading off data consistency and the amount of synced records. In the case of the API of The Guardian, news articles tend to only be updated for a few days after the initial release date, so this strategy should be able to catch most updates without having to resync all articles.

Reiterating the example from above with a "Lookback window" of 2 days configured, let's assume the last encountered article looked like this:

```json
{`{
  "id": "business/live/2023/apr/15/uk-bosses-more-optimistic-energy-prices-fall-ai-spending-boom-economics-business-live",
  "type": "liveblog",
  "sectionId": "business",
  "sectionName": "Business",
  "webPublicationDate": `}<b>{`"2023-04-15T07:30:58Z"`}</b>{`,
}`}
```

Then when a sync is triggered for the same connection the next day, the following request is made:

```bash
curl 'https://content.guardianapis.com/search?from-date=<b>2023-04-13T07:30:58Z</b>&to-date={`<now>`}'
```

## Custom parameter injection

Using the "Inject start time / end time into outgoing HTTP request" option in the incremental sync form works for most cases, but sometimes the API has special requirements that can't be handled this way:

- The API requires adding a prefix or a suffix to the actual value
- Multiple values need to be put together in a single parameter
- The value needs to be injected into the URL path
- Some conditional logic needs to be applied

To handle these cases, disable injection in the incremental sync form and use the generic parameter section at the bottom of the stream configuration form to freely configure query parameters, headers and properties of the JSON body, by using jinja expressions and [available variables](/platform/connector-development/config-based/understanding-the-yaml-file/reference/#/variables). You can also use these variables as part of the URL path.

For example the [Sendgrid API](https://docs.sendgrid.com/api-reference/e-mail-activity/filter-all-messages) requires setting both start and end time in a `query` parameter.
For this case, you can use the `stream_interval` variable to configure a query parameter with "key" `query` and "value" `last_event_time BETWEEN TIMESTAMP "{{stream_interval.start_time}}" AND TIMESTAMP "{{stream_interval.end_time}}"` to filter down to the right window in time.
