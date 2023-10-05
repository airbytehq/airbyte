# Medallia

This page contains the setup guide and reference information for the Medallia source connector.

## Prerequisites

The [Medallia GraphQL API](https://developer.medallia.com/medallia-apis/reference/query-api-overview) is used to get the survey feedback and fields data.

## Setup guide
### Step 1: Set up Medallia

To use this connector you will need to be a customer of Medallia and have access to create a service account. 

The Medallia Experience Cloud APIs use OAuth 2.0 for authenticating access to data and API endpoints. To access Medallia APIs, you will need a client ID and a client secret. 
[Reference the product documentation for creating these.](https://docs.medallia.com/en/medallia-experience-cloud/administration/security/oauth)

## Step 2: Set up the Medallia connector in Airbyte

### For Airbyte Open Source:
1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source
3. Enter your oAuth Client ID
4. Enter your oAuth Client Secret
5. Enter your Medallia Query Endpoint
6. Enter your Medallia oAuth Token Endpoint
7. Click **Set up source**

## Supported sync modes

The Medallia source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ |:-----------|
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |


## Supported Streams

This Source is capable of syncing the following Klarna Settlements Streams:

* [Fields](https://developer.medallia.com/medallia-apis/reference/query-api-overview#fields)
* [Feedback](https://developer.medallia.com/medallia-apis/reference/query-api-overview#invitations-and-feedback)

## Performance considerations

Medallia API has [rate limiting](https://developer.medallia.com/medallia-apis/reference/query-api-overview)

Query API is subject to the following rate limits:

* 10 requests per second.
* 150,000 requests per 24-hour window.
* 40,000,000 cost units per 60-second window (as measured using the X-Medallia-Query-Cost response header).

## Changelog

| Version | Date       | Pull Request                                             | Subject                          |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------|
| 0.1.0   | 2023-07-12 | [27245](https://github.com/airbytehq/airbyte/pull/27245)   | Medallia API (Fields & Feedback) |
