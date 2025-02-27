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
| 0.1.32 | 2025-02-22 | [54370](https://github.com/airbytehq/airbyte/pull/54370) | Update dependencies |
| 0.1.31 | 2025-02-15 | [53713](https://github.com/airbytehq/airbyte/pull/53713) | Update dependencies |
| 0.1.30 | 2025-02-01 | [52834](https://github.com/airbytehq/airbyte/pull/52834) | Update dependencies |
| 0.1.29 | 2025-01-25 | [52296](https://github.com/airbytehq/airbyte/pull/52296) | Update dependencies |
| 0.1.28 | 2025-01-18 | [51705](https://github.com/airbytehq/airbyte/pull/51705) | Update dependencies |
| 0.1.27 | 2025-01-11 | [51111](https://github.com/airbytehq/airbyte/pull/51111) | Update dependencies |
| 0.1.26 | 2024-12-28 | [50577](https://github.com/airbytehq/airbyte/pull/50577) | Update dependencies |
| 0.1.25 | 2024-12-21 | [50039](https://github.com/airbytehq/airbyte/pull/50039) | Update dependencies |
| 0.1.24 | 2024-12-14 | [49207](https://github.com/airbytehq/airbyte/pull/49207) | Update dependencies |
| 0.1.23 | 2024-11-25 | [48636](https://github.com/airbytehq/airbyte/pull/48636) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.22 | 2024-11-04 | [48221](https://github.com/airbytehq/airbyte/pull/48221) | Update dependencies |
| 0.1.21 | 2024-10-28 | [47056](https://github.com/airbytehq/airbyte/pull/47056) | Update dependencies |
| 0.1.20 | 2024-10-12 | [46776](https://github.com/airbytehq/airbyte/pull/46776) | Update dependencies |
| 0.1.19 | 2024-10-05 | [46466](https://github.com/airbytehq/airbyte/pull/46466) | Update dependencies |
| 0.1.18 | 2024-09-28 | [46128](https://github.com/airbytehq/airbyte/pull/46128) | Update dependencies |
| 0.1.17 | 2024-09-21 | [45724](https://github.com/airbytehq/airbyte/pull/45724) | Update dependencies |
| 0.1.16 | 2024-09-14 | [45545](https://github.com/airbytehq/airbyte/pull/45545) | Update dependencies |
| 0.1.15 | 2024-09-07 | [45302](https://github.com/airbytehq/airbyte/pull/45302) | Update dependencies |
| 0.1.14 | 2024-08-31 | [44963](https://github.com/airbytehq/airbyte/pull/44963) | Update dependencies |
| 0.1.13 | 2024-08-24 | [44689](https://github.com/airbytehq/airbyte/pull/44689) | Update dependencies |
| 0.1.12 | 2024-08-17 | [44335](https://github.com/airbytehq/airbyte/pull/44335) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43651](https://github.com/airbytehq/airbyte/pull/43651) | Update dependencies |
| 0.1.10 | 2024-08-03 | [43187](https://github.com/airbytehq/airbyte/pull/43187) | Update dependencies |
| 0.1.9 | 2024-07-27 | [42797](https://github.com/airbytehq/airbyte/pull/42797) | Update dependencies |
| 0.1.8 | 2024-07-20 | [42370](https://github.com/airbytehq/airbyte/pull/42370) | Update dependencies |
| 0.1.7 | 2024-07-13 | [41902](https://github.com/airbytehq/airbyte/pull/41902) | Update dependencies |
| 0.1.6 | 2024-07-10 | [41438](https://github.com/airbytehq/airbyte/pull/41438) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40945](https://github.com/airbytehq/airbyte/pull/40945) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40383](https://github.com/airbytehq/airbyte/pull/40383) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40142](https://github.com/airbytehq/airbyte/pull/40142) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39256](https://github.com/airbytehq/airbyte/pull/39256) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38450](https://github.com/airbytehq/airbyte/pull/38450) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2023-04-27 | [25598](https://github.com/airbytehq/airbyte/pull/25598) | Use region specific API server |
| 0.1.0 | 2022-10-06 | [17559](https://github.com/airbytehq/airbyte/pull/17559) | The Genesys Source is created |

</details>
