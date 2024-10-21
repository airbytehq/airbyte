# Slab
Slab source connector for ingesting data from the slab API.
Slab is a platform to easily create, organise, and discover knowledge for your entire organisation, from non-technical to tech-savvy. https://slab.com/

In order to use this source, you must first create an account and log in. 
The API uses a bearer token which can be obtained by navigating to Settings -&gt; Developer -&gt; Admin Token.
You must be on a the business plan to obtain a token.
Slab uses Graphql API and this connector streams the `users`, `posts` and `topics` endpoints. Find more information about the API here https://studio.apollographql.com/public/Slab/variant/current/home 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | start_date. Date from when the sync should start |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | No pagination | ✅ |  ❌  |
| topics | id | No pagination | ✅ |  ❌  |
| posts | post_id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-11 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
