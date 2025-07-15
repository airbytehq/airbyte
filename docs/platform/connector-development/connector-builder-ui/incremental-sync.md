# Incremental sync

An incremental sync is a sync which pulls only the data that has changed since the previous sync (as opposed to all the data available in the data source).

This is especially important if there are a large number of records to sync and/or the API has tight request limits which makes a full sync of all records on a regular schedule too expensive or too slow.

Incremental syncs are usually implemented using a cursor value (like a timestamp) that delineates which data was pulled and which data is new. A very common cursor value is an `updated_at` timestamp. This cursor means that records whose `updated_at` value is less than or equal than that cursor value have been synced already, and that the next sync should only export records whose `updated_at` value is greater than the cursor value.

To use incremental syncs, the API endpoint needs to fulfill the following requirements:

- Records contain a top-level date/time field that defines when this record was last updated (the "cursor field")
  - If the record's cursor field is nested, you can use an "Add Field" transformation to copy it to the top-level, and a Remove Field to remove it from the object. This will effectively move the field to the top-level of the record
- It's possible to filter/request records by the cursor field

The knowledge of a cursor value also allows the Airbyte system to automatically keep a history of changes to records in the destination. To learn more about how different modes of incremental syncs, check out the [Incremental Sync - Append](/platform/using-airbyte/core-concepts/sync-modes/incremental-append/) and [Incremental Sync - Append + Deduped](/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) pages.

## Incremental Sync Types

The Connector Builder supports three types of incremental sync implementations:

### Datetime-Based Cursor (Most Common)
Uses a datetime field to track which records have been synced. This is the most common type and what's described in the main configuration section below.

### Incrementing Count Cursor  
Uses a continuously increasing integer field (like an auto-incrementing ID) to track sync progress. Useful when your API doesn't have reliable datetime fields but has sequential numeric identifiers.

### Custom Incremental Sync
For advanced use cases that require custom logic not covered by the standard cursor types. This requires implementing custom Python code.

## Configuration

:::info Advanced Mode
This documentation describes the incremental sync configuration as it appears when **Advanced mode** is enabled in the Connector Builder. Advanced mode provides access to all available configuration options. If you're using the basic mode, some of these options may be grouped differently or hidden in collapsible sections.
:::

To configure incremental syncs for a stream in the connector builder, you have to specify how the records will represent the **"last changed" / "updated at" timestamp**, the **initial time range** to fetch records for and **how to request records from a certain time range**.

In the Advanced mode UI, these things are specified like this:

- The **"Cursor Field"** is the property in the record that defines the date and time when the record got changed. It's used to decide which records are synced already and which records are "new"
- The **"Cursor Datetime Formats"** specifies one or more formats that the cursor field might use. The connector will try each format in order until it finds one that matches. This is useful when your API returns dates in multiple formats across different records.
- The **"Start Datetime"** is the initial start date of the time range to fetch records for. When doing incremental syncs, subsequent syncs will use the last cursor value from the previous sync.
- The **"End Datetime"** is the end date of the time range to fetch records for. In most cases it's set to the current date and time when the sync is started.
- The **"Start Time Option"** defines how to send the start datetime values to the API. Options include query parameters, headers, or request body fields.
- The **"End Time Option"** defines how to send the end datetime values to the API. Options include query parameters, headers, or request body fields.
- The **"Datetime Format"** specifies the format used when sending datetime values in API requests.

## Cursor Datetime Formats

The Connector Builder can automatically detect and parse datetime values in various formats. You can specify multiple formats in order of preference - the connector will try each format until it finds one that matches your data.

Common datetime formats include:
- `%Y-%m-%dT%H:%M:%S.%f%z` - ISO 8601 with microseconds and timezone (e.g., "2023-04-15T07:30:58.123456+00:00")
- `%Y-%m-%dT%H:%M:%SZ` - ISO 8601 with Z timezone (e.g., "2023-04-15T07:30:58Z")  
- `%Y-%m-%d %H:%M:%S` - Standard datetime (e.g., "2023-04-15 07:30:58")
- `%Y-%m-%d` - Date only (e.g., "2023-04-15")
- `%s` - Unix timestamp in seconds (e.g., "1681542658")
- `%ms` - Unix timestamp in milliseconds (e.g., "1681542658123")

The UI will suggest detected formats based on your test data, making it easy to configure the right format for your API.

## Advanced Configuration Options

When Advanced mode is enabled in the Connector Builder, additional configuration options become available for fine-tuning incremental sync behavior:

### Data Feed Configuration
- **"Is Data Feed"**: Enable this when the API doesn't support filtering and returns data from newest to oldest. This replaces the previous "API time filtering capabilities" dropdown.
- **"Is Client Side Incremental"**: Enable when the API doesn't support cursor-based filtering and returns all data. The connector will filter records locally.

### Performance Optimization  
- **"Global Substream Cursor"**: Store cursor as one value instead of per partition. Optimizes performance when the parent stream has thousands of partitions.
- **"Is Compare Strictly"**: Skip requests if the start time equals the end time. Useful for APIs that don't accept queries where start equals end time.

### Date Range Clamping
- **"Clamping"**: Adjust datetime window boundaries to the beginning and end of specified periods (day, week, month).
  - **Target**: The period to clamp by (e.g., "DAY", "WEEK", "MONTH")

### Partition Configuration
- **"Partition Field Start"**: Name of the partition start time field (e.g., "starting_time")
- **"Partition Field End"**: Name of the partition end time field (e.g., "ending_time")

These advanced options provide fine-grained control over incremental sync behavior for complex API requirements.

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

As this fulfills the requirements for incremental syncs, we can configure the incremental sync section in the following way:

- "Cursor Field" is set to `webPublicationDate`
- "Cursor Datetime Formats" includes `%Y-%m-%dT%H:%M:%SZ`
- "Datetime Format" is set to `%Y-%m-%dT%H:%M:%SZ`
- "Start Datetime" is set to "user input" to allow the user of the connector configuring a Source to specify the time to start syncing
- "End Datetime" is set to "now" to fetch all articles up to the current date
- "Start Time Option" is set to `request_parameter` with "Field Name" set to `from-date`
- "End Time Option" is set to `request_parameter` with "Field Name" set to `to-date`

<iframe width="640" height="835" src="https://www.loom.com/embed/78eb5da26e2e4f4aa9c3a48573d9ed3b" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

Setting the start date in the "Testing values" to a date in the past like **2023-04-09T00:00:00Z** results in the following request:

<pre>
curl 'https://content.guardianapis.com/search?from-date=<b>2023-04-09T00:00:00Z</b>&to-date={`now`}'
</pre>

The most recent encountered date will be saved as the [*state*](../../understanding-airbyte/airbyte-protocol.md#state--checkpointing) of the connection - when the next sync is running, it picks up from that cutoff date as the new start date. Let's assume the last encountered article looked like this:

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
curl 'https://content.guardianapis.com/search?from-date=<b>2023-04-15T07:30:58Z</b>&to-date={`<now>`}'
</pre>

:::info
If the last record read has a datetime earlier than the end time of the stream interval, the end time of the interval will be stored in the state.
:::

The `from-date` is set to the cutoff date of articles synced already and the `to-date` is set to the current date.

:::info
In some cases, it's helpful to reference the start and end date of the interval that's currently synced, for example if it needs to be injected into the URL path of the current stream. In these cases it can be referenced using the `{{ stream_interval.start_time }}` and `{{ stream_interval.end_time }}` [placeholders](/platform/connector-development/config-based/understanding-the-yaml-file/reference#variables). Check out [the tutorial](./tutorial.mdx#adding-incremental-reads) for such a case.
:::

## Incremental sync without time filtering (Data Feed Mode)

Some APIs do not allow filtering records by a date field, but instead only provide a paginated "feed" of data that is ordered from newest to oldest. In Advanced mode, enable the **"Is Data Feed"** option for these cases.

When this option is enabled:
- The "Start Time Option" and "End Time Option" fields are disabled
- The "Split up interval" advanced option is disabled  
- The connector will automatically paginate through records until it encounters a cursor value that is less than or equal to the cutoff date from the previous sync

The `/new` endpoint of the [Reddit API](https://www.reddit.com/dev/api/#GET_new) is such an API. By enabling the "Is Data Feed" option and configuring pagination, the connector will automatically request the next page of records until the cutoff datetime is encountered.

:::warning
The "Is Data Feed" option can only be used if the data is sorted from newest to oldest across pages. If the data is sorted differently, the connector will stop syncing records too late or too early. In these cases it's better to disable incremental syncs and sync the full set of records on a regular schedule.
:::

## Advanced settings

The description above is sufficient for a lot of APIs. However there are some more subtle configurations which sometimes become relevant.

### Split up interval

When incremental syncs are enabled and "Split Up Interval" is configured, the connector splits the time range between the cutoff date and the desired end date into smaller intervals. This requires two settings:

- **"Step"**: The size of each time interval expressed as an [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations) (e.g., `P10D` for 10 days, `PT1H` for 1 hour)
- **"Cursor Granularity"**: The smallest time unit the API supports for filtering, also as an ISO 8601 duration (e.g., `PT1S` for 1 second, `P1D` for 1 day)

The cursor granularity ensures that intervals don't overlap. For example, if the granularity is 1 second (`PT1S`), then when one interval ends at `2023-01-09T23:59:59Z`, the next interval will start at `2023-01-10T00:00:00Z`.

For example if the "Step" is set to 10 days (`P10D`) and the "Cursor granularity" set to one second (`PT1S`) for the Guardian articles stream described above and a longer time range, then the following requests will be performed:

<pre>
curl 'https://content.guardianapis.com/search?from-date=<b>2023-01-01T00:00:00Z</b>&to-date=<b>2023-01-09T23:59:59Z</b>'{`\n`}
curl 'https://content.guardianapis.com/search?from-date=<b>2023-01-10T00:00:00Z</b>&to-date=<b>2023-01-19T23:59:59Z</b>'{`\n`}
curl 'https://content.guardianapis.com/search?from-date=<b>2023-01-20T00:00:00Z</b>&to-date=<b>2023-01-29T23:59:59Z</b>'{`\n`}
...
</pre>

After an interval is processed, the cursor value of the last record will be saved as part of the connection as the new cutoff date, as described in the [example above](#example).

If "Split Up Interval" is left unset, the connector will not split up the time range at all but will instead just request all records for the entire target time range. This configuration works for all connectors, but there are two reasons to change it:

- **To protect a connection against intermittent failures** - if the "Step" size is a day, the cutoff date is saved after all records associated with a day are processed. If a sync fails halfway through because the API, the Airbyte system, the destination or the network between these components has a failure, then at most one day worth of data needs to be resynced. However, a smaller step size might cause more requests to the API and more load on the system. It depends on the expected amount of data and load characteristics of an API what step size is optimal, but for a lot of applications the default of one month is a good starting point.
- **The API requires the connector to fetch data in pre-specified chunks** - for example the [Exchange Rates API](https://exchangeratesapi.io/documentation/) makes the date to fetch data for part of the URL path and only allows to fetch data for a single day at a time

### Lookback window

The **"Lookback Window"** specifies a duration that is subtracted from the last cutoff date before starting to sync.

Some APIs update records over time but do not allow to filter or search by modification date, only by creation date. For example the API of The Guardian might change the title of an article after it got published, but the `webPublicationDate` still shows the original date the article got published initially.

In these cases, there are two options:

- **Do not use incremental sync** and always sync the full set of records to always have a consistent state, losing the advantages of reduced load and [automatic history keeping in the destination](/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)
- **Configure the "Lookback Window"** to not only sync exclusively new records, but resync some portion of records before the cutoff date to catch changes that were made to existing records, trading off data consistency and the amount of synced records. In the case of the API of The Guardian, news articles tend to only be updated for a few days after the initial release date, so this strategy should be able to catch most updates without having to resync all articles.

Reiterating the example from above with a "Lookback Window" of 2 days configured, let's assume the last encountered article looked like this:

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
curl 'https://content.guardianapis.com/search?from-date=<b>2023-04-13T07:30:58Z</b>&to-date={`<now>`}'
</pre>

## Custom parameter injection

Using the "Start Time Option" and "End Time Option" fields in the incremental sync form works for most cases, but sometimes the API has special requirements that can't be handled this way:

- The API requires adding a prefix or a suffix to the actual value
- Multiple values need to be put together in a single parameter
- The value needs to be injected into the URL path
- Some conditional logic needs to be applied

To handle these cases, disable injection in the incremental sync form and use the generic parameter section at the bottom of the stream configuration form to freely configure query parameters, headers and properties of the JSON body, by using jinja expressions and [available variables](/platform/connector-development/config-based/understanding-the-yaml-file/reference/#/variables). You can also use these variables as part of the URL path.

For example the [Sendgrid API](https://docs.sendgrid.com/api-reference/e-mail-activity/filter-all-messages) requires setting both start and end time in a `query` parameter.
For this case, you can use the `stream_interval` variable to configure a query parameter with "key" `query` and "value" `last_event_time BETWEEN TIMESTAMP "{{stream_interval.start_time}}" AND TIMESTAMP "{{stream_interval.end_time}}"` to filter down to the right window in time.

## Incrementing Count Cursor

For APIs that use continuously increasing integer values (like auto-incrementing IDs) instead of datetime fields, you can use an Incrementing Count Cursor. This is useful when:

- Your API doesn't have reliable datetime fields
- Records have sequential numeric identifiers  
- The API supports filtering by numeric ranges

### Configuration
- **"Cursor Field"**: The field containing the incrementing integer value (e.g., "id", "sequence_number")
- **"Start Datetime"**: The initial value to start syncing from (e.g., 0, 1, or a specific ID)
- **"Start Time Option"**: How to send the cursor value in API requests (query parameter, header, etc.)

### Example
If your API has records with incrementing IDs and supports a `since_id` parameter:
```json
{
  "id": 12345,
  "name": "Example Record",
  "data": "..."
}
```

You would configure:
- "Cursor Field": `id`
- "Start Datetime": `0` (or the ID you want to start from)
- "Start Time Option": Query parameter named `since_id`

The connector will track the highest ID seen and use it as the starting point for the next sync.
