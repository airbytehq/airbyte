# Metabase

This page contains the setup guide and reference information for the Metabase source connector.

## Prerequisites

To set up Metabase you need:

- `username` and `password` - Credential pairs to authenticate with Metabase instance. This may be used to generate a new `session_token` if necessary. An email from Metabase may be sent to the owner's account every time this is being used to open a new session.
- `session_token` - Credential token to authenticate requests sent to Metabase API. Usually expires after 14 days.
- `instance_api_url` - URL to interact with Metabase instance API, that uses https.

## Setup guide

You can find or create authentication tokens from [Metabase](https://www.metabase.com/learn/administration/metabase-api.html#authenticate-your-requests-with-a-session-token) by running the following command:`

```bash
curl -X POST \
-H "Content-Type: application/json" \
-d '{"username": "person@metabase.com", "password": "fakepassword"}' \
http://localhost:3000/api/session
```

If you’re working with a remote server, you’ll need to replace localhost:3000 with your server address. This request will return a JSON object with a key called id and the token as the key’s value, e.g.:

```
{"id":"38f4939c-ad7f-4cbe-ae54-30946daf8593"}
```

You can use this id value as your `session_token` when configuring the connector.
Note that these credentials tokens may expire after 14 days by default, and you might need to update your connector configuration with a new value when that happens (The connector should throw exceptions about Invalid and expired session tokens and return a 401 (Unauthorized) status code in that scenario).

If you are hosting your own Metabase instance, you can configure this session duration on your Metabase server by setting the environment variable MAX_SESSION_AGE (value is in minutes).

If the connector is supplied with only username and password, a session_token will be generated every time an
authenticated query is running, which might trigger security alerts on the user's Metabase account.

## Supported sync modes

The Metabase source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)

## Supported Streams

- [Card](https://www.metabase.com/docs/latest/api/card.html#get-apicard)
- [Collections](https://www.metabase.com/docs/latest/api/collection.html#get-apicollection)
- [Dashboard](https://www.metabase.com/docs/latest/api/dashboard.html#get-apidashboard)
- [User](https://www.metabase.com/docs/latest/api/user.html#get-apiuser)
- [Databases](https://www.metabase.com/docs/latest/api/user.html#get-apiuser)
- [Native Query Snippet](https://www.metabase.com/docs/latest/api/native-query-snippet#get-apinative-query-snippetid)

## Tutorials

### Data type mapping

| Integration Type    | Airbyte Type | Notes |
| :------------------ | :----------- | :---- |
| `string`            | `string`     |       |
| `integer`, `number` | `number`     |       |
| `array`             | `array`      |       |
| `object`            | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| SSL connection    | Yes                  |       |
| Namespaces        | No                   |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| 2.1.14 | 2025-02-22 | [54326](https://github.com/airbytehq/airbyte/pull/54326) | Update dependencies |
| 2.1.13 | 2025-02-15 | [53791](https://github.com/airbytehq/airbyte/pull/53791) | Update dependencies |
| 2.1.12 | 2025-02-08 | [53288](https://github.com/airbytehq/airbyte/pull/53288) | Update dependencies |
| 2.1.11 | 2025-02-01 | [52735](https://github.com/airbytehq/airbyte/pull/52735) | Update dependencies |
| 2.1.10 | 2025-01-25 | [52258](https://github.com/airbytehq/airbyte/pull/52258) | Update dependencies |
| 2.1.9 | 2025-01-18 | [51841](https://github.com/airbytehq/airbyte/pull/51841) | Update dependencies |
| 2.1.8 | 2025-01-11 | [51218](https://github.com/airbytehq/airbyte/pull/51218) | Update dependencies |
| 2.1.7 | 2024-12-28 | [50616](https://github.com/airbytehq/airbyte/pull/50616) | Update dependencies |
| 2.1.6 | 2024-12-21 | [50089](https://github.com/airbytehq/airbyte/pull/50089) | Update dependencies |
| 2.1.5 | 2024-12-14 | [49215](https://github.com/airbytehq/airbyte/pull/49215) | Update dependencies |
| 2.1.4 | 2024-12-11 | [48982](https://github.com/airbytehq/airbyte/pull/48982) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.1.3 | 2024-10-29 | [47776](https://github.com/airbytehq/airbyte/pull/47776) | Update dependencies |
| 2.1.2 | 2024-10-28 | [47531](https://github.com/airbytehq/airbyte/pull/47531) | Update dependencies |
| 2.1.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 2.1.0 | 2024-08-15 | [44127](https://github.com/airbytehq/airbyte/pull/44127) | Refactor connector to manifest-only format |
| 2.0.13 | 2024-08-12 | [43857](https://github.com/airbytehq/airbyte/pull/43857) | Update dependencies |
| 2.0.12 | 2024-08-10 | [43685](https://github.com/airbytehq/airbyte/pull/43685) | Update dependencies |
| 2.0.11 | 2024-08-03 | [43156](https://github.com/airbytehq/airbyte/pull/43156) | Update dependencies |
| 2.0.10 | 2024-07-27 | [42798](https://github.com/airbytehq/airbyte/pull/42798) | Update dependencies |
| 2.0.9 | 2024-07-20 | [42314](https://github.com/airbytehq/airbyte/pull/42314) | Update dependencies |
| 2.0.8 | 2024-07-16 | [38347](https://github.com/airbytehq/airbyte/pull/38347) | Make connector compatible with the builder |
| 2.0.7 | 2024-07-13 | [41816](https://github.com/airbytehq/airbyte/pull/41816) | Update dependencies |
| 2.0.6 | 2024-07-10 | [41471](https://github.com/airbytehq/airbyte/pull/41471) | Update dependencies |
| 2.0.5 | 2024-07-09 | [41171](https://github.com/airbytehq/airbyte/pull/41171) | Update dependencies |
| 2.0.4 | 2024-07-06 | [40940](https://github.com/airbytehq/airbyte/pull/40940) | Update dependencies |
| 2.0.3 | 2024-06-26 | [40528](https://github.com/airbytehq/airbyte/pull/40528) | Update dependencies |
| 2.0.2 | 2024-06-22 | [40117](https://github.com/airbytehq/airbyte/pull/40117) | Update dependencies |
| 2.0.1 | 2024-06-06 | [39205](https://github.com/airbytehq/airbyte/pull/39205) | [autopull] Upgrade base image to v1.2.2 |
| 2.0.0 | 2024-03-01 | [35680](https://github.com/airbytehq/airbyte/pull/35680) | Updates `dashboards` stream, Base image migration: remove Dockerfile and use the python-connector-base image, migrated to poetry |
| 1.1.0 | 2023-10-31 | [31909](https://github.com/airbytehq/airbyte/pull/31909) | Add `databases` and `native_query_snippets` streams |
| 1.0.1   | 2023-07-20 | [28470](https://github.com/airbytehq/airbyte/pull/27777) | Update CDK to 0.47.0                                                                                                             |
| 1.0.0   | 2023-06-27 | [27777](https://github.com/airbytehq/airbyte/pull/27777) | Remove Activity Stream                                                                                                           |
| 0.3.1   | 2022-12-15 | [20535](https://github.com/airbytehq/airbyte/pull/20535) | Run on CDK 0.15.0                                                                                                                |
| 0.3.0   | 2022-12-13 | [19236](https://github.com/airbytehq/airbyte/pull/19236) | Migrate to YAML.                                                                                                                 |
| 0.2.0   | 2022-10-28 | [18607](https://github.com/airbytehq/airbyte/pull/18607) | Disallow using `http` URLs                                                                                                       |
| 0.1.0   | 2022-06-15 | [6975](https://github.com/airbytehq/airbyte/pull/13752)  | Initial (alpha) release                                                                                                          |

</details>
