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

| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.3 | 2024-04-18 | [37165](https://github.com/airbytehq/airbyte/pull/37165) | Manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37165](https://github.com/airbytehq/airbyte/pull/37165) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37165](https://github.com/airbytehq/airbyte/pull/37165) | schema descriptions |
| 0.1.0 | 2022-10-06 | [17559](https://github.com/airbytehq/airbyte/pull/17559) | The Genesys Source is created |
