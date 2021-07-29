# HTTP Request

## Overview

This source allows you to make any http request an Airbyte source! On each sync, this source makes a single http request to the provided URL. Whatever json body is returned is written to the destination.

#### Output schema

It contains one stream: `data`. That stream will contain one record which is the json blob returned by the http request.

#### Data type mapping

`data` is a json blob.

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |
| Namespaces | No |

### Getting started

#### Setup guide

Provide a url, http\_method, \(optional\) headers, \(optional\) request body. The source will make exactly this http request.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.4   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE_ENTRYPOINT for Kubernetes support |
| 0.2.3   | 2021-04-20 | [3165](https://github.com/airbytehq/airbyte/pull/3165) | Version bump |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.1.1   | 2021-03-07 | [2342](https://github.com/airbytehq/airbyte/pull/2342) | Fix incorrect documentation |
| 0.1.0   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |
