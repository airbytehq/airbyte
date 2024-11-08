# NewsData.io
Connector for NewsData.io to get the latest news in pagination and the latest news from specific countries, categories and domains. You can also get the news sources from specific categories, countries and languages.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `apikey` | `string` | apiKey.  |  |
| `category` | `string` | category.  |  |
| `countrycode` | `string` | countryCode.  |  |
| `languagecode` | `string` | languageCode.  |  |
| `countrycodes` | `string` | countryCodes.  |  |
| `domain` | `string` | domain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Latest News |  | DefaultPaginator | ✅ |  ❌  |
| News Sources From Specific Category |  | No pagination | ✅ |  ❌  |
| News Sources From Specific Country |  | No pagination | ✅ |  ❌  |
| News Sources From Specific Language |  | No pagination | ✅ |  ❌  |
| Latest News From Specific Countries |  | No pagination | ✅ |  ❌  |
| Latest News From Specific Domain |  | No pagination | ✅ |  ❌  |
| Latest News From Specific Category |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@faria-karim-porna](https://github.com/faria-karim-porna) via Connector Builder |

</details>
