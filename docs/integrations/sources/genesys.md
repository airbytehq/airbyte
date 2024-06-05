# Genesys

## Overview

The Genesys source retrieves data from [Genesys](https://www.genesys.com/) using their [JSON REST APIs](https://developer.genesys.cloud/devapps/api-explorer).

## Setup Guide

### Requirements

We are using `OAuth2` as this is the only supported authentication method. So you will need to follow the steps below to generate the `Client ID` and `Client Secret`.

- Genesys region
- Client ID
- Client Secret

You can follow the documentation on [API credentials](https://developer.genesys.cloud/authorization/platform-auth/use-client-credentials#obtain-an-access-token) or you can login directly to the [OAuth admin page](https://apps.mypurecloud.com/directory/#/admin/integrations/oauth)

## Supported Streams

- [Locations](https://developer.genesys.cloud/telephony/locations-apis)
- [Routing](https://developer.genesys.cloud/routing/routing/)
- [Stations](https://developer.genesys.cloud/telephony/stations-apis)
- [Telephony](hhttps://developer.genesys.cloud/telephony/telephony-apis)
- [Users](https://developer.genesys.cloud/useragentman/users/)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.1.1 | 2024-05-20 | [38450](https://github.com/airbytehq/airbyte/pull/38450) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2023-04-27 | [25598](https://github.com/airbytehq/airbyte/pull/25598) | Use region specific API server |
| 0.1.0 | 2022-10-06 | [17559](https://github.com/airbytehq/airbyte/pull/17559) | The Genesys Source is created |

</details>