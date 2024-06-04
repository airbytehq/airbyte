# News API

## Sync overview

This source retrieves news stories from the [News API](https://newsapi.org/).
It can retrieve news stories all news stories found within the parameters
chosen, or just top headlines.

### Output schema

This source is capable of syncing the following streams:

- `everything`
- `top_headlines`

### Features

| Feature           | Supported? \(Yes/No\) | Notes |
| :---------------- | :-------------------- | :---- |
| Full Refresh Sync | Yes                   |       |
| Incremental Sync  | No                    |       |

### Performance considerations

The News API free tier only allows 100 requests per day, and only up to 100
results per request. It is not recommended to attempt to use this source with
a free tier API key.

## Getting started

### Requirements

1. A News API key. You can get one [here](https://newsapi.org/). It is
   highly recommended to use a paid tier key.

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your News API key.
- (optional) `search_query`: A search query to filter the results by. For more
  information on constructing a search query, see the
  [News API documentation](https://newsapi.org/docs/endpoints/everything).
- (optional) `search_in`: Fields to search in. Possible values are `title`,
  `description` and `content`.
- (optional) `sources`: Sources to search in. For a list of sources, see the
  [News API documentation](https://newsapi.org/sources).
- (optional) `domains`: Domains to search in.
- (optional) `exclude_domains`: Domains to exclude from the search.
- (optional) `start_date`: The start date to search from.
- (optional) `end_date`: The end date to search to.
- (optional) `language`: The language to search in.
- `country`: The country you want headlines for.
- `category`: The category you want headlines for.
- `sort_by`: How to sort the results.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                  |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------- |
| 0.1.2 | 2024-05-20 | [38418](https://github.com/airbytehq/airbyte/pull/38418) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2023-04-30 | [25554](https://github.com/airbytehq/airbyte/pull/25554) | Make manifest connector builder friendly |
| 0.1.0 | 2022-10-21 | [18301](https://github.com/airbytehq/airbyte/pull/18301) | New source |

</details>