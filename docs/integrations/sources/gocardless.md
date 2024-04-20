# GoCardless

## Overview

The GoCardless source can sync data from the [GoCardless API](https://gocardless.com/)

#### Output schema

This source is capable of syncing the following streams:
* Mandates
* Payments
* Payouts
* Refunds


#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Namespaces | No |

### Requirements / Setup Guide
* Access Token
* GoCardless Environment
* GoCardless Version
* Start Date


## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2024-04-19 | [0](https://github.com/airbytehq/airbyte/pull/0) | Manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37168](https://github.com/airbytehq/airbyte/pull/37168) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37168](https://github.com/airbytehq/airbyte/pull/37168) | schema descriptions |
| 0.1.0 | 2022-10-19 | [17792](https://github.com/airbytehq/airbyte/pull/17792) | Initial release supporting the GoCardless |
