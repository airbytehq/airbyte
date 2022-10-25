# UK Police

## Sync overview

This source retrieves crime and stop and search data from the
[UK Police Data API](https://data.police.uk/docs/).

### Output schema

This source is capable of syncing the following streams:

* `all_forces`
* `crime_categories`
* `street_level_crime`
* `street_level_outcomes`
* `crimes_at_location`
* `crimes_with_no_location`
* `stop_and_search_for_area`
* `stop_and_search_with_no_location`
* `stop_and_search_for_force`

### Features

| Feature           | Supported? \(Yes/No\) | Notes |
|:------------------|:----------------------|:------|
| Full Refresh Sync | Yes                   |       |
| Incremental Sync  | No                    |       |

### Performance considerations

The Police Data API has a rate limit of 15 requests per second, with a burst
limit of 30 requests per second. The source should not run into these under
normal operation.

## Getting started

### Requirements

1. Choose a start date (in `yyyy-mm` format) to sync data from
2. Find the latitude and longitude of your area of interest

### Setup guide

The following fields are required fields for the connector to work:

- `start_year_month`: The start date to sync data from (in `yyyy-mm` format)
- (optional) `end_year_month`: The end date to sync data to (in `yyyy-mm` 
  format). Defaults to the current month
- `crime_category`: The crime category to filter by. Defaults to all crime 
  categories
- `lat`: The latitude of your area of interest
- `lng`: The longitude of your area of interest
- (optional) `force`: The police force to filter by for `*_no_location` and
  `*_by_force` streams.

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.0   | 2022-10-23 | [18344](https://github.com/airbytehq/airbyte/pull/18344) | New source |
