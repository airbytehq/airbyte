# Zendesk Chat

This page contains the setup guide and reference information for Zendesk Chat.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Incremental - Append | Yes |
| Incremental - Deduped | Yes |

## Prerequisites

* A Zendesk account with an Administrator role
* Zendesk Access Token
* Zendesk subdomain

## Setup guide

### Step 1: Create the OAuth API client

Follow these [instructions](https://support.zendesk.com/hc/en-us/articles/4408828740762-Chat-API-tutorial-Generating-an-OAuth-token-integrated-Chat-accounts-) or the below steps to **Add API client**. This process will produce the `client id` and `client secret` you will need to generate the `access token` needed to set up the source in Daspire.

1. Inside your Zendesk Chat account in the left navbar, click **Settings**, then click **Account**.
![Zendesk Chat API Client](/docs/setup-guide/assets/images/zendesk-chat-api-client.jpg "Zendesk Chat API Client")

2. Click **Add API client**.

3. Enter a name for the client and company of your choosing, and for the Redirect URL. You can use `http://localhost:8080` as the Redirect URL. Once done, click **Create API client**.
![Zendesk Chat Create API Token](/docs/setup-guide/assets/images/zendesk-chat-create-api-token.jpg "Zendesk Chat Create API Token")

4. You will be shown a popup with the **Client ID** and **Client secret**.
![Zendesk Chat Client Details](/docs/setup-guide/assets/images/zendesk-chat-client-details.jpg "Zendesk Chat Client Details")

  NOTE: The client secret is shown only once, so make a note of it for later use.

### Step 2: Obtain the Access token

1. Format the below URL with your own **CLIENT_ID** which you obtained in step 1 and your Zendesk **SUBDOMAIN**.
```
https://www.zopim.com/oauth2/authorizations/new?response_type=token&client_id=CLIENT_ID&scope=read%20write&subdomain=SUBDOMAIN
```

2. Paste it into a new browser tab, and press Enter.

3. The call will be made, possibly asking you to log in and select **Allow** to generate the token.
![Zendesk Chat OAuth](/docs/setup-guide/assets/images/zendesk-chat-oauth.jpg "Zendesk Chat OAuth")

4. If the call succeeds, your browser's address field will contain your **access_token**. Copy it.
![Zendesk Chat Access Token](/docs/setup-guide/assets/images/zendesk-chat-access-token.jpg "Zendesk Chat Access Token")

### Step 3: Set up Zendesk Chat in Daspire

1. Select **Zendesk Chat** from the Source list.

2. Enter a **Source Name**.

3. To authenticate your account, select **Access Token** and enter the Access Token you generated in Step 2.

4. For **Subdomain**, enter your Zendesk subdomain. This is the subdomain found in your account URL. For example, if your account URL is `https://MY_SUBDOMAIN.zendesk.com/`, then `MY_SUBDOMAIN` is your subdomain.

5. (Optional) For **Start Date**, enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated. If this field is left blank, Daspire will replicate the data for the last two years by default.

6. Click **Save & Test**.

## Output schema

This Source is capable of syncing the following core Streams:

* [Account](https://developer.zendesk.com/rest_api/docs/chat/accounts#show-account)
* [Agents](https://developer.zendesk.com/rest_api/docs/chat/agents#list-agents) (Incremental)
* [Agent Timelines](https://developer.zendesk.com/rest_api/docs/chat/incremental_export#incremental-agent-timeline-export) (Incremental)
* [Chats](https://developer.zendesk.com/rest_api/docs/chat/chats#list-chats)
* [Shortcuts](https://developer.zendesk.com/rest_api/docs/chat/shortcuts#list-shortcuts)
* [Triggers](https://developer.zendesk.com/rest_api/docs/chat/triggers#list-triggers)
* [Bans](https://developer.zendesk.com/rest_api/docs/chat/bans#list-bans) (Incremental)
* [Departments](https://developer.zendesk.com/rest_api/docs/chat/departments#list-departments)
* [Goals](https://developer.zendesk.com/rest_api/docs/chat/goals#list-goals)
* [Skills](https://developer.zendesk.com/rest_api/docs/chat/skills#list-skills)
* [Roles](https://developer.zendesk.com/rest_api/docs/chat/roles#list-roles)
* [Routing Settings](https://developer.zendesk.com/rest_api/docs/chat/routing_settings#show-account-routing-settings)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Performance considerations

The integration is restricted by normal [Zendesk requests limitation](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#rate-limit). The integration ideally should not run into Zendesk API limitations under normal usage.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
