# Typeform

## Overview

The Zapier Supported Storage Connector can be used to sync your [Zapier](https://store.zapier.com/) data

#### Output schema

This Source is capable of syncing the following Streams:

* [Forms](https://developer.typeform.com/create/reference/retrieve-form/) \(Full Refresh\)
* [Responses](https://developer.typeform.com/responses/reference/retrieve-responses/) \(Incremental\)
* [Webhooks](https://developer.typeform.com/webhooks/reference/retrieve-webhooks/) \(Full Refresh\)
* [Workspaces](https://developer.typeform.com/create/reference/retrieve-workspaces/) \(Full Refresh\)
* [Images](https://developer.typeform.com/create/reference/retrieve-images-collection/) \(Full Refresh\)
* [Themes](https://developer.typeform.com/create/reference/retrieve-themes/) \(Full Refresh\)

#### Data type mapping

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |
| `boolean`        | `boolean`    |       |

#### Features

| Feature                   | Supported? |
|:--------------------------|:-----------|
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

### Requirements

* secret - The Storage by Zapier secret.

### Setup guide

To get the API token for your application follow this [steps](https://developer.typeform.com/get-started/personal-access-token/)

* Log in to your account at Typeform.
* In the upper-right corner, in the drop-down menu next to your profile photo, click My Account.
* In the left menu, click Personal tokens.
* Click Generate a new token.
* In the Token name field, type a name for the token to help you identify it.
* Choose needed scopes \(API actions this token can perform - or permissions it has\). See here for more details on scopes.
* Click Generate token.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|                        |
| 0.1.0   | 2022-10-25 | [18442](https://github.com/airbytehq/airbyte/pull/18442)  | Initial release|

