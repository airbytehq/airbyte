# Typeform

## Overview

The Typeform Connector can be used to sync your [Typeform](https://developer.typeform.com/get-started/) data

Useful links:

* [Token generation](https://developer.typeform.com/get-started/personal-access-token/)

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

* token - The Typeform API key token.
* start\_date - Date to start fetching Responses stream data from.
* form_ids (Optional) - List of Form Ids to sync. If not passed - sync all account`s forms.

### Setup guide

To get the API token for your application follow this [steps](https://developer.typeform.com/get-started/personal-access-token/)

* Log in to your account at Typeform.
* In the upper-right corner, in the drop-down menu next to your profile photo, click My Account.
* In the left menu, click Personal tokens.
* Click Generate a new token.
* In the Token name field, type a name for the token to help you identify it.
* Choose needed scopes \(API actions this token can perform - or permissions it has\). See here for more details on scopes.
* Click Generate token.

## Performance considerations

Typeform API page size limit per source:

* Forms - 200
* Responses - 1000

Connector performs additional API call to fetch all possible `form ids` on an account using [retrieve forms endpoint](https://developer.typeform.com/create/reference/retrieve-forms/)

API rate limits \(2 requests per second\): [https://developer.typeform.com/get-started/\#rate-limits](https://developer.typeform.com/get-started/#rate-limits)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.1.8   | 2022-08-09 | [15435](https://github.com/airbytehq/airbyte/pull/15435) | Update Forms   stream schema                                            |
| 0.1.7   | 2022-06-20 | [13935](https://github.com/airbytehq/airbyte/pull/13935) | Update Responses stream schema                                          |
| 0.1.6   | 2022-05-23 | [12280](https://github.com/airbytehq/airbyte/pull/12280) | Full Stream Coverage                                                    |
| 0.1.4   | 2021-12-08 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                |
| 0.1.3   | 2021-12-07 | [8466](https://github.com/airbytehq/airbyte/pull/8466)   | Change Check Connection Function Logic                                  |
| 0.1.2   | 2021-10-11 | [6571](https://github.com/airbytehq/airbyte/pull/6571)   | Support pulling data from a select set of forms                         |
| 0.1.1   | 2021-09-06 | [5799](https://github.com/airbytehq/airbyte/pull/5799)   | Add missed choices field to responses schema                            |
| 0.1.0   | 2021-07-10 | [4541](https://github.com/airbytehq/airbyte/pull/4541)   | Initial release for Typeform API supporting Forms and Responses streams |

