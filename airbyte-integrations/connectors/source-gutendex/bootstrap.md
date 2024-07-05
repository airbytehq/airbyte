# Gutendex

## Overview

Project Gutenberg is a volunteer effort to digitize and archive cultural works, as well as to "encourage the creation and distribution of eBooks." It was founded in 1971 by American writer Michael S. Hart and is the oldest digital library. It has over 60,000 books

[Gutendex](https://gutendex.com/) is a JSON web API for Project Gutenberg eBook metadata. The Gutendex Connector is implemented with the [Airbyte Low-Code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).

## Output Format

#### Each Book has the following structure

```yaml
{
  "id": <number of Project Gutenberg ID>,
  "title": <string>,
  "authors": <array of Persons>,
  "translators": <array of Persons>,
  "subjects": <array of strings>,
  "bookshelves": <array of strings>,
  "languages": <array of strings>,
  "copyright": <boolean or null>,
  "media_type": <string>,
  "formats": <Format>,
  "download_count": <number>,
}
```

#### Each Person has the following structure

```yaml
{
  "birth_year": <number or null>,
  "death_year": <number or null>,
  "name": <string>,
}
```

## Core Streams

Connector supports the `books` stream that provides information and metadata about books matching the query.

## Rate Limiting

No published rate limit.

## Authentication and Permissions

No authentication.

See [this](https://docs.airbyte.io/integrations/sources/gutendex) link for the connector docs.
