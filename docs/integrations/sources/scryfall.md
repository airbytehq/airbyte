# Scryfall
For Magic The Gathering fans. Here is a simple data source for all the cards and sets!

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| cards | id | DefaultPaginator | ✅ |  ❌  |
| sets | id | No pagination | ✅ |  ❌  |
| symbols | symbol | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-08-28 | | Initial release by [@michel-tricot](https://github.com/michel-tricot) via Connector Builder |

</details>