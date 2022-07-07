# Facebook Pages

## Sync overview

The Facebook Pages source uses [Facebook Graph API](https://developers.facebook.com/docs/graph-api/?locale=en_US) to read data from the Facebook social graph.

### Output schema

This Source is capable of syncing the following core Streams:

* [Page](https://developers.facebook.com/docs/graph-api/reference/v11.0/page/#fields)
* [Post](https://developers.facebook.com/docs/graph-api/reference/v11.0/page/feed#pubfields)
* [Page Insights](https://developers.facebook.com/docs/graph-api/reference/v11.0/page/insights/#fields)
* [Post Insights](https://developers.facebook.com/docs/graph-api/reference/v11.0/insights)

The linked Facebook docs go into detail about the fields present on those streams.

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
| Incremental Sync | No |  |
| Namespaces | No |  |

### Rate Limiting & Performance Considerations

Facebook heavily throttles API tokens generated from Facebook Apps by default, making it infeasible to use such a token for syncs with Airbyte. To be able to use this connector without your syncs taking days due to rate limiting follow the instructions in the Setup Guide below to access better rate limits.

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting) for more information on requesting a quota upgrade.

## Getting started

### Requirements

* A Facebook Developer Account
* A Facebook App
* A Facebook API Page Access Token
* A Facebook `Page` ID

### Setup guide

### Facebook Developer Account

Follow the [Facebook Developer Account ](https://developers.facebook.com/async/registration/) link to create new account.

### Facebook App

#### If you don't have a Facebook App

Visit the [Facebook Developers App hub](https://developers.facebook.com/apps/) and create an App and choose "Company" as the purpose of the app. Fill out the remaining fields to create your app, then follow along the "Connect a User Page" section.

#### Connect a User Page

Follow the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) link. 1. Choose your app at `Facebook App` field 2. Choose your Page at `User or Page` field 3. Add next permission:

* pages\_read\_engagement
* pages\_read\_user\_content 
* pages\_show\_list
* read\_insights
  1. Click Generate Access Token and follow instructions.

After all the steps, it should look something like this

![](../../.gitbook/assets/facebook-pages-1.png)

Now can copy your Access Token from `Access Token` field \(This is a short live Page access token, if you need a long-lived Page access token, you can [generate](https://developers.facebook.com/docs/facebook-login/access-tokens/refreshing#get-a-long-lived-page-access-token) one from a long-lived User access token. Long-lived Page access token do not have an expiration date and only expire or are invalidated under certain conditions.\)

#### Getting Page ID

You can easily get the page id from the page url. For example, if you have a page URL such as `https://www.facebook.com/Test-1111111111`, the ID would be`Test-1111111111`.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.6 | 2021-12-22 | [9032](https://github.com/airbytehq/airbyte/pull/9032) | Remove deprecated field `live_encoders` from Page stream |
| 0.1.5 | 2021-11-26 | [8267](https://github.com/airbytehq/airbyte/pull/) | updated all empty objects in schemas for Page and Post streams |
| 0.1.4 | 2021-11-26 | [](https://github.com/airbytehq/airbyte/pull/) | Remove unsupported insights_export field from Pages request |
| 0.1.3 | 2021-10-28 | [7440](https://github.com/airbytehq/airbyte/pull/7440) | Generate Page token from config access token |
| 0.1.2 | 2021-10-18 | [7128](https://github.com/airbytehq/airbyte/pull/7128) | Upgrade Facebook API to v.12 |
| 0.1.1 | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438) | Annotate Oauth2 flow initialization parameters in connector specification |
| 0.1.0 | 2021-09-01 | [5158](https://github.com/airbytehq/airbyte/pull/5158) | Initial Release |
