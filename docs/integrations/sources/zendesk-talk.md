# Zendesk Talk

## Sync overview

The Zendesk Talk source supports Full Refresh syncs.

This source can sync data for the [Zendesk Talk API](https://developer.zendesk.com/rest_api/docs/voice-api/introduction).

### Output schema

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

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits).

The Zendesk connector should not run into Zendesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Zendesk API Token 
* Zendesk Email 
* Zendesk Subdomain 

### Setup guide

Generate a API access token as described in [Zendesk docs](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

### CHANGELOG

| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.3` | 2021-11-11 | [7173](https://github.com/airbytehq/airbyte/pull/7173) | Fix pagination and migrate to CDK |
