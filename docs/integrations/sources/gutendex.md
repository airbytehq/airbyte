# Gutendex

## Overview

The Gutendex source can sync data from the [Gutendex API](https://gutendex.com/)

## Requirements

Gutendex requires no access token/API key to make requests.
The following (optional) parameters can be provided to the connector :-

---

##### `author_year_start` and `author_year_end`

Use these to find books with at least one author alive in a given range of years. They must have positive (CE) or negative (BCE) integer values.

For example, `/books?author_year_start=1800&author_year_end=1899` gives books with authors alive in the 19th Century.

---

##### `copyright`

Use this to find books with a certain copyright status: true for books with existing copyrights, false for books in the public domain in the USA, or null for books with no available copyright information.

---

##### `languages`

Use this to find books in any of a list of languages. They must be comma-separated, two-character language codes. For example, `/books?languages=en` gives books in English, and `/books?languages=fr,fi` gives books in either French or Finnish or both.

---

##### `search`

Use this to search author names and book titles with given words. They must be separated by a space (i.e. %20 in URL-encoded format) and are case-insensitive. For example, `/books?search=dickens%20great` includes Great Expectations by Charles Dickens.

---

##### `sort`

Use this to sort books: ascending for Project Gutenberg ID numbers from lowest to highest, descending for IDs highest to lowest, or popular (the default) for most popular to least popular by number of downloads.

---

##### `topic`

Use this to search for a case-insensitive key-phrase in books' bookshelves or subjects. For example, `/books?topic=children` gives books on the "Children's Literature" bookshelf, with the subject "Sick children -- Fiction", and so on.

---

## Output schema

Lists of book information in the Project Gutenberg database are queried using the API at /books (e.g. gutendex.com/books). Book data will be returned in the format:-

```
{
    "count": <number>,
    "next": <string or null>,
    "previous": <string or null>,
    "results": <array of Books>
}
```

where `results` is an array of 0-32 book objects, next and previous are URLs to the next and previous pages of results, and count in the total number of books for the query on all pages combined.

By default, books are ordered by popularity, determined by their numbers of downloads from Project Gutenberg.

The source is capable of syncing the results stream.

## Setup guide

## Step 1: Set up the Gutendex connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, select **Gutendex** from the Source type dropdown.
4. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source (Gutendex).
3. Click **Set up source**.

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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.1 | 2024-05-21 | [38509](https://github.com/airbytehq/airbyte/pull/38509) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-17 | [#18075](https://github.com/airbytehq/airbyte/pull/18075) | 🎉 New Source: Gutendex API [low-code CDK] |

</details>