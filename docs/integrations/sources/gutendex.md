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

| Version | Date       | Pull Request                                              | Subject                                     |
| :------ |:-----------| :-------------------------------------------------------- |:--------------------------------------------|
| 0.2.2 | 2025-02-22 | [54345](https://github.com/airbytehq/airbyte/pull/54345) | Update dependencies |
| 0.2.1 | 2025-02-15 | [48316](https://github.com/airbytehq/airbyte/pull/48316) | Update dependencies |
| 0.2.0 | 2024-08-23 | [44617](https://github.com/airbytehq/airbyte/pull/44617) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-17 | [44264](https://github.com/airbytehq/airbyte/pull/44264) | Update dependencies |
| 0.1.14 | 2024-08-12 | [43924](https://github.com/airbytehq/airbyte/pull/43924) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43562](https://github.com/airbytehq/airbyte/pull/43562) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43258](https://github.com/airbytehq/airbyte/pull/43258) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42701](https://github.com/airbytehq/airbyte/pull/42701) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42278](https://github.com/airbytehq/airbyte/pull/42278) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41827](https://github.com/airbytehq/airbyte/pull/41827) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41507](https://github.com/airbytehq/airbyte/pull/41507) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41244](https://github.com/airbytehq/airbyte/pull/41244) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40823](https://github.com/airbytehq/airbyte/pull/40823) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40394](https://github.com/airbytehq/airbyte/pull/40394) | Update dependencies |
| 0.1.4 | 2024-06-23 | [39924](https://github.com/airbytehq/airbyte/pull/39924) | Update dependencies |
| 0.1.3 | 2024-06-15 | [39509](https://github.com/airbytehq/airbyte/pull/39509) | Make connector compatible with Builder |
| 0.1.2 | 2024-06-04 | [39017](https://github.com/airbytehq/airbyte/pull/39017) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38509](https://github.com/airbytehq/airbyte/pull/38509) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-17 | [#18075](https://github.com/airbytehq/airbyte/pull/18075) | 🎉 New Source: Gutendex API [low-code CDK]  |

</details>
