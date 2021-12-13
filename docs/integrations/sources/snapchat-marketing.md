# Snapchat Marketing

## Overview

The Snapchat Marketing source can sync data from the [Snapchat Marketing API](https://marketingapi.snapchat.com/docs/)

Useful links:

* [Snapchat Ads Manager](https://ads.snapchat.com/)  
* [Snapchat API Docs](https://marketingapi.snapchat.com/docs/)
* [Snapchat API FAQ](https://businesshelp.snapchat.com/s/article/api-faq?language=en_US)
* [Set up Snapchat Business account](https://businesshelp.snapchat.com/s/article/get-started?language=en_US)
* [Activate Access to the Snapchat Marketing API](https://businesshelp.snapchat.com/s/article/api-apply?language=en_US)

#### Output schema

This Source is capable of syncing the following Streams:

* [Organization](https://marketingapi.snapchat.com/docs/#organizations)
* [Ad Account](https://marketingapi.snapchat.com/docs/#get-all-ad-accounts) \(Incremental\)
* [Creative](https://marketingapi.snapchat.com/docs/#get-all-creatives) \(Incremental\)
* [Media](https://marketingapi.snapchat.com/docs/#get-all-media) \(Incremental\)
* [Campaign](https://marketingapi.snapchat.com/docs/#get-all-campaigns) \(Incremental\)
* [Ad](https://marketingapi.snapchat.com/docs/#get-all-ads-under-an-ad-account) \(Incremental\)
* [Ad Squad](https://marketingapi.snapchat.com/docs/#get-all-ad-squads-under-an-ad-account) \(Incremental\)
* [Segments](https://marketingapi.snapchat.com/docs/#get-all-audience-segments) \(Incremental\)

#### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `integer` | `integer` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |
| `boolean` | `boolean` |  |

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

### Requirements

* client\_id - Snapchat account client ID
* client\_secret - Snapchat account client secret
* refresh\_token - Snapchat account refresh token 

### Setup guide

To get the required credentials you need to set up a snapchat business account. Follow this guide to set up one:

* [Set up Snapchat Business account](https://businesshelp.snapchat.com/s/article/get-started?language=en_US)
* After that - [Activate Access to the Snapchat Marketing API](https://businesshelp.snapchat.com/s/article/api-apply?language=en_US)  
* Adding the OAuth2 app requires the `redirect_url` parameter. If you have the API endpoint that will handle next OAuth process - write it to this parameter. 

  If not - just use some valid url. Here's the discussion about it: [Snapchat Redirect URL - Clarity in documentation please](https://github.com/Snap-Kit/bitmoji-sample/issues/3) 

* On this step you will retrieve **Client ID** and **Client Secret** carefully save **Client Secret** - you cannot view it in UI, only by regenerating

Snapchat uses OAuth2 authentication, so to get the refresh token the workflow in next: 1. Open the authorize link in a browser: [https://accounts.snapchat.com/login/oauth2/authorize?response\_type=code&client\_id={client\_id}&redirect\_uri={redirect\_uri}&scope=snapchat-marketing-api&state=wmKkg0TWgppW8PTBZ20sldUmF7hwvU](https://accounts.snapchat.com/login/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=snapchat-marketing-api&state=wmKkg0TWgppW8PTBZ20sldUmF7hwvU)

1. Login & Authorize via UI
2. Locate "code" query parameter in the redirect
3. Exchange code for access token + refresh token

   ```text
   curl -X POST \  
   -d "code={one_time_use_code}" \  
   -d "client_id={client_id}" \  
   -d "client_secret={client_secret}"  \  
   -d "grant_type=authorization_code"  \  
   -d "redirect_uri=redirect_uri"  
   https://accounts.snapchat.com/login/oauth2/access_token
   ```

You will receive the API key and refresh token in response. Use this refresh token in the connector specifications.  
The useful link to Authentication process is [here](https://marketingapi.snapchat.com/docs/#authentication)

## Performance considerations

Snapchat Marketing API has limitations to 1000 items per page

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2021-11-10 | [7811](https://github.com/airbytehq/airbyte/pull/7811) | Add oauth2.0, fix stream_state |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.1 | 2021-07-29 | [5072](https://github.com/airbytehq/airbyte/pull/5072) | Fix bug with incorrect stream\_state value |
| 0.1.0 | 2021-07-26 | [4843](https://github.com/airbytehq/airbyte/pull/4843) | Initial release supporting the Snapchat Marketing API |

