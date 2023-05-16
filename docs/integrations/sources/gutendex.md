# Gutendex

## Overview

The Gutendex source can sync data from the [Gutendex API](https://gutendex.com/).

## Requirements

Gutendex requires no access token/API key to make requests. The following (optional) parameters can be provided to the connector: 

| Parameter | Optional/Required | Description |
|-----------|------------------|-------------|
| author_year_start | Optional | Defines the minimum birth year of the authors. Books by authors born prior to the start year will not be returned. Supports both positive (CE) or negative (BCE) integer values. |
| author_year_end | Optional | Defines the maximum birth year of the authors. Books by authors born after the end year will not be returned. Supports both positive (CE) or negative (BCE) integer values. |
| copyright | Optional | Use this to find books with a certain copyright status: `true` for books with existing copyrights, `false` for books in the public domain in the USA, or `null` for books with no available copyright information. |
| languages | Optional | Use this to find books in any of a list of languages. They must be comma-separated, two-character language codes. |
| search | Optional | Use this to search author names and book titles with given words. They must be separated by a space (i.e. `%20` in URL-encoded format) and are case-insensitive. |
| sort | Optional | Use this to sort books - `ascending` for Project Gutenberg ID numbers from lowest to highest, `descending` for IDs highest to lowest, or `popular` (the default) for most popular to least popular by number of downloads. |
| topic | Optional | Use this to search for a case-insensitive key-phrase in books' bookshelves or subjects. |

## Output schema

Lists of book information in the Project Gutenberg database are queried using the API at `/books` (e.g. `gutendex.com/books`). Book data will be returned in the format:

```json
{
    "count": <number>,
    "next": <string or null>,
    "previous": <string or null>,
    "results": <array of Books>
}
```

`results` is an array of 0-32 book objects, `next` and `previous` are URLs to the next and previous pages of results, and `count` is the total number of books for the query on all pages combined.

By default, books are ordered by popularity, determined by their numbers of downloads from Project Gutenberg.

The source is capable of syncing the results stream.

## Setup guide

This guide assumes you have already navigated to the Gutendex connector set up page in Airbyte.

1. Enter a name for the connection.
2. Provide any of the optional parameters in the configuration section as necessary to refine the data returned from Gutendex.
    - `author_year_start`: Defines the minimum birth year of the authors. Books by authors born prior to the start year will not be returned.
    - `author_year_end`: Defines the maximum birth year of the authors. Books by authors born after the end year will not be returned.
    - `copyright`: Use this to find books with a certain copyright status - `true` for books with existing copyrights, `false` for books in the public domain in the USA, or `null` for books with no available copyright information.
    - `languages`: Use this to find books in any of a list of languages. They must be comma-separated, two-character language codes.
    - `search`: Use this to search author names and book titles with given words. They must be separated by a space (i.e. `%20` in URL-encoded format) and are case-insensitive.
    - `sort`: Use this to sort books - `ascending` for Project Gutenberg ID numbers from lowest to highest, `descending` for IDs highest to lowest, or `popular` (the default) for most popular to least popular by number of downloads.
    - `topic`: Use this to search for a case-insensitive key-phrase in books' bookshelves or subjects.
3. Enter the URL `https://api.gutendex.com/books` into the "Endpoint" field.
4. Verify the "Output Schema" to ensure it meets your use case.
5. Click "Test Connection" to verify the connection between Airbyte and Gutendex.
6. Click "Create Connection" to complete the connection setup.

### Obtaining confirmation

No confirmation is necessary to set up the Gutendex connector in Airbyte.

## Supported sync modes

The Gutendex source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Performance considerations

There is no published rate limit. However, since this data updates infrequently, it is recommended to set the update cadence to 24hr or higher.

## Changelog

Please see the existing Changelog in the provided documentation.