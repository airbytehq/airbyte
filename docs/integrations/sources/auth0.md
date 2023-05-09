# Auth0

Auth0 is a flexible, drop-in solution to add authentication and authorization services to your applications.

The source connector fetches data from [Auth0 Management API](https://auth0.com/docs/api/authentication#introduction)

## Prerequisites

* You own an Auth0 account, free or paid.
* Follow the [Setup guide](#setup-guide) to authorize Airbyte to read data from your account.

## Setup guide

### Step 1: Set up an Auth0 account

1. It's free to [sign up an account](https://auth0.com/signup) in Auth0.
2. Confirm your Email.

### Step 2.1: Get an Access Tokens for Testing

1. In Auth0, go to [the Api Explorer tab of your Auth0 Management API](https://manage.auth0.com/#/apis/management/explorer). A token is automatically generated and displayed there.
2. Click **Copy Token**.
3. In Airbyte, choose **OAuth2 Access Token** under the **Authentication Method** menu, Paste the token to the text box of **OAuth2 Access Token**
4. Click **Save** to test the connectivity.
5. More details can be found from [this documentation](https://auth0.com/docs/secure/tokens/access-tokens/get-management-api-access-tokens-for-testing).

### Step 2.2: Create a new app for OAuth2

1. To make scheduled frequent calls for a production environment, you have setup an OAuth2 integration so that Airbyte can generate the access token automatically.
2. In Auth0, go to [Dashboard > Applications > Applications](https://manage.auth0.com/?#/applications).
3. Create a new application, name it **Airbyte**. Choose the application type **Machine to Machine Applications**
4. Select the Management API V2, this is the api you want call from Airbyte.
5. Each M2M app that accesses an API must be granted a set of permissions (or scopes). Here, we only need permissions starting with `read` (e.g. *read:users*). Under the [API doc](https://auth0.com/docs/api/management/v2#!/Users/get_users), each api will list the required scopes.
6. More details can be found from [this documentation](https://auth0.com/docs/secure/tokens/access-tokens/get-management-api-access-tokens-for-production).

## Supported sync modes

The Auth0 source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental

## Supported Streams

- [Users](https://auth0.com/docs/api/management/v2#!/Users/get_users)

## Performance considerations

The connector is restricted by Auth0 [rate limits](https://auth0.com/docs/troubleshoot/customer-support/operational-policies/rate-limit-policy/management-api-endpoint-rate-limits).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                        |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------|
| 0.1.0  | 2022-10-21 | TBD | Add Auth0 and Users stream |
