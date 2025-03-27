# MyPoke
MyPoke is a PokeAPI clone made for the purpose of investigating https://github.com/airbytehq/airbyte-internal-issues/issues/12043

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `pokemon_name` | `string` | Pokemon Name. Pokemon requested from the API. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| pokemon | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-03-27 | | Initial release by [@dbgold17](https://github.com/dbgold17) via Connector Builder |

</details>
