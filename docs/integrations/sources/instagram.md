# Instagram

## Sync overview

This source can sync data for the Instagram Business Account available in the Facebook Graph API: User, Media, and Stories. It can also sync Media/Story and User Insights.

### Output schema

This Source is capable of syncing the following core Streams:

* [User](https://developers.facebook.com/docs/instagram-api/reference/ig-user)
  * [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
* [Media](https://developers.facebook.com/docs/instagram-api/reference/ig-user/media)
  * [Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)
* [Stories](https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories/)
  * [Story Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

For more information, see the [Instagram API](https://developers.facebook.com/docs/instagram-api/) and [Instagram Insights API documentation](https://developers.facebook.com/docs/instagram-api/guides/insights/).

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |
| Namespaces | No |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes | only User Insights |

### Rate Limiting & Performance Considerations

Instagram, like all Facebook services, has a limit on the number of requests, but Instagram connector gracefully handles rate limiting.

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/#instagram-graph-api) for more information.

## Getting started

### Requirements

* A Facebook App
* An Instagram Business Account
* A Facebook Page linked to your Instagram Business Account
* A Facebook API Access Token

### Setup guide

### Facebook App

#### If you don't have a Facebook App

Visit the [Facebook Developers App hub](https://developers.facebook.com/apps/) and create an App and choose "Manage Business Integrations" as the purpose of the app. Fill out the remaining fields to create your app.

### Facebook Page

See the Facebook [support](https://www.facebook.com/business/help/898752960195806) for information about how to add an Instagram Account to your Facebook Page.

### Instagram Business Account

Follow the [Instagram documentation](https://www.facebook.com/business/help/1492627900875762) for setting up an Instagram business account. We'll need this ID to configure Instagram as a source in Airbyte.

### API Access Token

To work with the Instagram connector, you need to generate an Access Token with the following permissions:

* [instagram\_basic](https://developers.facebook.com/docs/permissions/reference/instagram_basic)
* [instagram\_manage\_insights](https://developers.facebook.com/docs/permissions/reference/instagram_manage_insights)
* [pages\_show\_list](https://developers.facebook.com/docs/permissions/reference/pages_show_list)
* [pages\_read\_engagement](https://developers.facebook.com/docs/permissions/reference/pages_read_engagement)
* [Instagram Public Content Access](https://developers.facebook.com/docs/apps/features-reference/instagram-public-content-access)

More details how to get a User's Access Token you can find in the following docs: [Access Tokens](https://developers.facebook.com/docs/facebook-login/access-tokens/#usertokens) and [User and Page Access Tokens](https://developers.facebook.com/docs/pages/access-tokens)

With the Instagram Account ID and API access token, you should be ready to start pulling data from the Facebook Instagram API. Head to the Airbyte UI to setup your source connector!

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.8  | 2021-08-11 | [5354](https://github.com/airbytehq/airbyte/pull/5354) | added check for empty state and fixed tests.|
| 0.1.7  | 2021-07-19 | [4805](https://github.com/airbytehq/airbyte/pull/4805) | Add support for previous format of STATE.|
| 0.1.6  | 2021-07-07 | [4210](https://github.com/airbytehq/airbyte/pull/4210) | Refactor connector to use CDK:<br>- improve error handling.<br>- fix sync fail with HTTP status 400.<br>- integrate SAT.|
