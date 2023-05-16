# Aha API

API Documentation link [here](https://www.aha.io/api)

## Overview

The Aha API source supports full refresh syncs.

### Output schema

Two output streams are available from this source:

- [features](https://www.aha.io/api/resources/features/list_features)
- [products](https://www.aha.io/api/resources/products/list_products_in_the_account)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

Rate Limiting information is updated [here](https://www.aha.io/api#rate-limiting).

## Getting started

### Requirements

- Aha API Key.

### Connect using `API Key`:

1. Generate an API Key by following the instructions provided in the [Aha API Authentication](https://www.aha.io/api#authentication) documentation.
2. Copy the generated `API Key`.
3. In Airbyte UI, navigate to the `Aha API` source connector page and click `Create New Connection`.
4. On the configuration page, enter a `Connection name` and paste the `API Key` into the `api_key` configuration field.
5. Enter your Aha organization's URL in the `url` configuration field.
6. Click `Check connection` to verify that Airbyte can connect to the Aha API with the provided credentials.
7. Click `Save`.

## Changelog

| Version | Date       | Pull Request                                             | Subject       |
| :------ | :--------- | :------------------------------------------------------- | :------------ |
| 0.1.0   | 2022-11-02 | [18893](https://github.com/airbytehq/airbyte/pull/18893) | 🎉 New Source |

---

**Note:** The information in this document is based on the current Aha interface. If there are any changes in the Aha API or UI, please refer to the Aha API documentation for updated information.