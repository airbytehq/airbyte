# Pocket

## Overview

The Pocket source connector only supports full refresh syncs

### Output schema

A single output stream is available from this source:

- [Retrieve](https://getpocket.com/developer/docs/v3/retrieve)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

For more info on rate limiting, please refer to [Pocket Docs > Rate Limits](https://getpocket.com/developer/docs/rate-limits)

## Getting started

### Requirements

- Consumer Key
- Access Token

### Setup Guide

In order to obtain the Consumer Key and Access Token, please follow the official [Pocket Authentication docs](https://getpocket.com/developer/docs/authentication).

It's nevertheless, very recommended to follow [this guide](https://www.jamesfmackenzie.com/getting-started-with-the-pocket-developer-api/) by James Mackenzie, which is summarized below:

1. Create an App in the [Pocket Developer Portal](https://getpocket.com/developer/apps/new), give it Retrieve permissions and get your Consumer Key.
2. Obtain a Request Token. To do so, you need to issue a POST request to get a temporary Request Token. You can execute the command below:

```sh
curl --insecure -X POST -H 'Content-Type: application/json' -H 'X-Accept: application/json' \
    https://getpocket.com/v3/oauth/request  -d '{"consumer_key":"REPLACE-ME","redirect_uri":"http://www.google.com"}'
```

3. Visit the following website from your browser, and authorize the app: `https://getpocket.com/auth/authorize?request_token=REPLACE-ME&redirect_uri=http://www.google.com`
4. Convert your Request Token Into a Pocket Access Token. To do so, you can execute the following command:

```sh
curl --insecure -X POST -H 'Content-Type: application/json' -H 'X-Accept: application/json' \
    https://getpocket.com/v3/oauth/authorize  -d '{"consumer_key":"REPLACE-ME","code":"REQUEST-TOKEN"}'
```

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.4 | 2024-06-06 | [39298](https://github.com/airbytehq/airbyte/pull/39298) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-04-19 | [37228](https://github.com/airbytehq/airbyte/pull/37228) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37228](https://github.com/airbytehq/airbyte/pull/37228) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37228](https://github.com/airbytehq/airbyte/pull/37228) | schema descriptions |
| 0.1.0 | 2022-10-30 | [18655](https://github.com/airbytehq/airbyte/pull/18655) | 🎉 New Source: Pocket |

</details>
