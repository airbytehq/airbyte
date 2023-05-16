# Gutendex

## Overview

The Gutendex source can sync data from the [Gutendex API](https://gutendex.com/)

## Requirements

Gutendex requires no access token/API key to make requests. The following (optional) parameters can be provided to the connector:

- `author_year_start` and `author_year_end`: Use these to find books with at least one author alive in a given range of years. They must have positive (CE) or negative (BCE) integer values.
- `copyright`: Use this to find books with a certain copyright status: true for books with existing copyrights, false for books in the public domain in the USA, or null for books with no available copyright information.
- `languages`: Use this to find books in any of a list of languages. They must be comma-separated, two-character language codes.
- `search`: Use this to search author names and book titles with given words. They must be separated by a space (i.e. %20 in URL-encoded format) and are case-insensitive.
- `sort`: Use this to sort books: ascending for Project Gutenberg ID numbers from lowest to highest, descending for IDs highest to lowest, or popular (the default) for most popular to least popular by number of downloads.
- `topic`: Use this to search for a case-insensitive key-phrase in books' bookshelves or subjects.

## Output schema

Lists of book information in the Project Gutenberg database are queried using the API at /books (e.g. gutendex.com/books). Book data will be returned in the format:-

    {
        "count": <number>,
        "next": <string or null>,
        "previous": <string or null>,
        "results": <array of Books>
    }

where `results` is an array of 0-32 book objects, next and previous are URLs to the next and previous pages of results, and count in the total number of books for the query on all pages combined.

By default, books are ordered by popularity, determined by their numbers of downloads from Project Gutenberg.

The source is capable of syncing the results stream.

## Setting up the Gutendex connector in Airbyte

Set up the Gutendex connector in Airbyte using the following steps:

1. Open the Airbyte connector setup for Gutendex
2. Fill out the connector specification form:

   - `author_year_start` and `author_year_end`: Use these to find books with at least one author alive in a given range of years. They must have positive (CE) or negative (BCE) integer values.
   - `copyright`: Use this to find books with a certain copyright status: true for books with existing copyrights, false for books in the public domain in the USA, or null for books with no available copyright information.
   - `languages`: Use this to find books in any of a list of languages. They must be comma-separated, two-character language codes.
   - `search`: Use this to search author names and book titles with given words. They must be separated by a space (i.e. %20 in URL-encoded format) and are case-insensitive.
   - `sort`: Use this to sort books: ascending for Project Gutenberg ID numbers from lowest to highest, descending for IDs highest to lowest, or popular (the default) for most popular to least popular by number of downloads.
   - `topic`: Use this to search for a case-insensitive key-phrase in books' bookshelves or subjects.

   See [Gutendex API Documentation](https://gutendex.com/api-docs) for more information on these parameters.

3. Once you have filled out the form, click **Test connection** to ensure that the required fields are correctly inputted and that you are getting the expected configuration response.
4. Click **Save** to complete the set up process.