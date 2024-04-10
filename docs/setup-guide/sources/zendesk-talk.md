# Zendesk Talk

This page contains the setup guide and reference information for Zendesk Talk.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |

## Prerequisites

* A Zendesk account with an Administrator role
* Zendesk API Token
* Zendesk subdomain

## Setup guide

### Step 1: Generate an API token

1. Inside your Zendesk account, click the Zendesk Products icon (four squares) in the top-right corner, then select **Admin Center**.
![Zendesk Admin Center](/docs/setup-guide/assets/images/zendesk-admin-center.jpg "Zendesk Admin Center")

2. In the left navbar, scroll down to **Apps and Integrations**, then select **APIs** > **Zendesk API**.
![Zendesk API](/docs/setup-guide/assets/images/zendesk-api.jpg "Zendesk API")

3. In the **Settings** tab, toggle the option to enable token access.
![Zendesk Enable Token Access](/docs/setup-guide/assets/images/zendesk-enable-token-access.jpg "Zendesk Enable Token Access")

4. Click the **Add API token** button. And then click Save.
![Zendesk API Token](/docs/setup-guide/assets/images/zendesk-api-token.jpg "Zendesk API Token")

  > CAUTION: Be sure to copy the token and save it in a secure location. You will not be able to access the token's value after you close the page.

### Step 2: Set up Zendesk Talk in Daspire

1. Select **Zendesk Talk** from the Source list.

2. Enter a **Source Name**.

3. To authenticate your account, select **API Token** and enter the API Token you generated in Step 1.

4. For **Subdomain**, enter your Zendesk subdomain. This is the subdomain found in your account URL. For example, if your account URL is `https://MY_SUBDOMAIN.zendesk.com/`, then `MY_SUBDOMAIN` is your subdomain.

5. (Optional) For **Start Date**, enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated. If this field is left blank, Daspire will replicate the data for the last two years by default.

6. Click **Save & Test**.

## Output schema

This Source is capable of syncing the following core Streams:

* [Account Overview](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-account-overview)
* [Addresses](https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers)
* [Agents Activity](https://developer.zendesk.com/rest_api/docs/voice-api/stats#list-agents-activity)
* [Agents Overview](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-agents-overview)
* [Calls](https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-calls-export) (Incremental)
* [Call Legs](https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-call-legs-export) (Incremental)
* [Current Queue Activity](https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-current-queue-activity)
* [Greeting Categories](https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greeting-categories)
* [Greetings](https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greetings)
* [IVRs](https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs)
* [IVR Menus](https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs)
* [IVR Routes](https://developer.zendesk.com/rest_api/docs/voice-api/ivr_routes#list-ivr-routes)
* [Phone Numbers](https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Performance considerations

The integration is restricted by normal [Zendesk requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits). The integration ideally should not run into Zendesk API limitations under normal usage.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
