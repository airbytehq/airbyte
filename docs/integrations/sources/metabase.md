# Metabase
This page contains the setup guide and reference information for the Metabase source connector.

## Prerequisites

To set up Metabase you need:
  * `username` and `password` - Credential pairs to authenticate with Metabase instance. This may be used to generate a new `session_token` if necessary. An email from Metabase may be sent to the owner's account everytime this is being used to open a new session.
  * `session_token` - Credential token to authenticate requests sent to Metabase API. Usually expires after 14 days.   
  * `instance_api_url` - URL to interact with metabase instance API, that uses https.

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

If you are hosting your own metabase instance, you can configure this session duration on your metabase server by setting the environment variable MAX_SESSION_AGE (value is in minutes).

If the connector is supplied with only username and password, a session_token will be generated everytime an
authenticated query is running, which might trigger security alerts on the user's metabase account.

## Supported sync modes

The Metabase source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)

## Supported Streams
* [Card](https://www.metabase.com/docs/latest/api/card.html#get-apicard)
* [Collections](https://www.metabase.com/docs/latest/api/collection.html#get-apicollection)
* [Dashboard](https://www.metabase.com/docs/latest/api/dashboard.html#get-apidashboard)
* [User](https://www.metabase.com/docs/latest/api/user.html#get-apiuser)

## Tutorials

### Data type mapping

| Integration Type    | Airbyte Type | Notes |
|:--------------------|:-------------|:------|
| `string`            | `string`     |       |
| `integer`, `number` | `number`     |       |
| `array`             | `array`      |       |
| `object`            | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
|:------------------|:---------------------|:------|
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| SSL connection    | Yes                  |
| Namespaces        | No                   |       |


## Changelog

| Version | Date       | Pull Request                                             | Subject                    |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------|
| 1.0.0   | 2023-06-27 | [27777](https://github.com/airbytehq/airbyte/pull/27777) | Remove Activity Stream     |
| 0.3.1   | 2022-12-15 | [20535](https://github.com/airbytehq/airbyte/pull/20535) | Run on CDK 0.15.0          |
| 0.3.0   | 2022-12-13 | [19236](https://github.com/airbytehq/airbyte/pull/19236) | Migrate to YAML.           |
| 0.2.0   | 2022-10-28 | [18607](https://github.com/airbytehq/airbyte/pull/18607) | Disallow using `http` URLs |
| 0.1.0   | 2022-06-15 | [6975](https://github.com/airbytehq/airbyte/pull/13752)  | Initial (alpha) release    |
