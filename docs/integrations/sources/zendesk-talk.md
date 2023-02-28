# Zendesk Talk

## Prerequisites

* Zendesk API Token or Zendesk OAuth Client
* Zendesk Email (For API Token authentication)
* Zendesk Subdomain

## Setup guide

### Step 1: Set up Zendesk

Generate a API access token as described in [Zendesk docs](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

Another option is to use OAuth2.0 for authentication. See [Zendesk docs](https://support.zendesk.com/hc/en-us/articles/4408845965210-Using-OAuth-authentication-with-your-application) for details.

<!-- env:cloud -->
### Step 2: Set up the Zendesk Talk connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Zendesk Talk connector and select **Zendesk Talk** from the Source type dropdown.
4. Fill in the rest of the fields:
   - *Subdomain*
   - *Authentication (API Token / OAuth2.0)*
   - *Start Date*
5. Click **Set up source**
<!-- /env:cloud -->

## Supported sync modes

The **Zendesk Talk** source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* Full Refresh
* Incremental Sync

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Account Overview](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-account-overview)
* [Addresses](https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers)
* [Agents Activity](https://developer.zendesk.com/rest_api/docs/voice-api/stats#list-agents-activity)
* [Agents Overview](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-agents-overview)
* [Calls](https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-calls-export) \(Incremental sync\)
* [Call Legs](https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-call-legs-export) \(Incremental sync\)
* [Current Queue Activity](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-current-queue-activity)
* [Greeting Categories](https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greeting-categories)
* [Greetings](https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greetings)
* [IVRs](https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs)
* [IVR Menus](https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs)
* [IVR Routes](https://developer.zendesk.com/rest_api/docs/voice-api/ivr_routes#list-ivr-routes)
* [Phone Numbers](https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers)

## Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits).

The Zendesk connector should not run into Zendesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Data type map

| Integration Type | Airbyte Type | Notes |
| :------- | :------- | :--- |
| `string` | `string` |      |
| `number` | `number` |      |
| `array`  | `array`  |      |
| `object` | `object` |      |


## Changelog


| Version | Date       | Pull Request | Subject                           |
|:--------|:-----------| :-----       |:----------------------------------|
| `0.1.6` | 2023-01-27 | [22028](https://github.com/airbytehq/airbyte/pull/22028) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| `0.1.5` | 2022-09-29 | [17362](https://github.com/airbytehq/airbyte/pull/17362) | always use the latest CDK version |
| `0.1.4` | 2022-08-19 | [15764](https://github.com/airbytehq/airbyte/pull/15764) | Support OAuth2.0                  |
| `0.1.3` | 2021-11-11 | [7173](https://github.com/airbytehq/airbyte/pull/7173)   | Fix pagination and migrate to CDK |
