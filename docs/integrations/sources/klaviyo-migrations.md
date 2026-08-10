# Klaviyo Migration Guide

## Upgrading to 3.0.0

This release changes the record shape of `flow_series_reports` and changes the reporting periods that both report streams request. Both streams need a schema refresh and a clear.

### What changed in `flow_series_reports`

The flow-series endpoint reports many days per response: it returns one `date_times` array plus, for each grouping, a statistics array whose values line up with that array by index. The connector used to emit one record per response, so each record carried whole arrays of daily values and a `date` copied from the end of the request window.

Now each response is split into one record per calendar day:

|                        | Before                                                                | After                                                       |
| ---------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------- |
| Records per grouping   | One per request window                                                | One per calendar day                                        |
| `statistics.opens`     | `[123, 156, 144]`                                                     | `144`                                                       |
| `date`                 | End of the request window, for example `2024-01-31T23:59:59+00:00`     | The day the row reports on, for example `2024-01-07T00:00:00+00:00` |

`groupings`, `flow_id`, `flow_message_id`, `send_channel` and `conversion_metric_id` are unchanged.

This is what makes the **Reporting Lookback Window (Days)** setting safe to use. The stream is keyed on `date` plus the grouping fields, so a day read again on a later sync arrives under the primary key it already had and replaces the row. Previously a re-read produced a new `date`, so the same days accumulated as extra rows and were counted twice. Set the lookback to at least your Klaviyo attribution window - 5 days by default, up to 90 days if you have raised it - to pick up conversion revisions.

### What changed in `campaign_values_reports`

The record shape is unchanged. Only the requested reporting periods change, as described below. There is deliberately no lookback window for this stream: it returns a single aggregate for the whole requested period rather than a per-day breakdown, so re-reading a period cannot replace an existing row and would only add a second row covering the same days.

### What changed in both streams

Report windows now always start at midnight UTC and cover whole calendar days. Klaviyo report timeframes are inclusive of both the first and the last day, so a window that stopped in the middle of a day reported that day, and so did the following window. With a start date carrying a time of day - for example `2017-01-25T09:30:00Z` - every 30-day window boundary therefore counted one day twice. Windows are now aligned to day boundaries, so each day belongs to exactly one window.

Because window boundaries move, the periods `campaign_values_reports` has already written no longer line up with the periods it writes from now on.

### Migration steps

1. Upgrade the connector to version 3.0.0.
2. In your connection, open the **Schema** tab and click **Refresh source schema**. Accept the changes for `flow_series_reports` and `campaign_values_reports`.
3. Clear both `flow_series_reports` and `campaign_values_reports` so they are re-read under the new record shape and the new window boundaries. Without this, old array-shaped rows and old reporting periods stay in your destination alongside the new ones.
4. Update any downstream models reading `flow_series_reports.statistics`. A field that was an array is now a single number, and there is one row per day instead of one row per sync window. Logic that used to unnest these arrays should now group by `date`.

Other streams are unaffected and do not need to be cleared.

## Upgrading to 2.0.0

Streams `campaigns`, `email_templates`, `events`, `flows`, `global_exclusions`, `lists`, and `metrics` are now pulling
data using latest API which has a different schema. Users will need to refresh the source schemas and reset these
streams after upgrading. See the chart below for the API version change.

| Stream            | Current API version | New API version |
|-------------------|---------------------|-----------------|
| campaigns         | v1                  | 2023-06-15      |
| email_templates   | v1                  | 2023-10-15      |
| events            | v1                  | 2023-10-15      |
| flows             | v1                  | 2023-10-15      |
| global_exclusions | v1                  | 2023-10-15      |
| lists             | v1                  | 2023-10-15      |
| metrics           | v1                  | 2023-10-15      |
| profiles          | 2023-02-22          | 2023-02-22      |

## Upgrading to 1.0.0

`event_properties/items/quantity` for `Events` stream is changed from `integer` to `number`.
For a smooth migration, data reset and schema refresh are needed.
