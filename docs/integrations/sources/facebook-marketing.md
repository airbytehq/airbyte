# Facebook Marketing

## Sync overview

This source can sync data for the core Ad Campaign data available in the [Facebook Marketing API](https://developers.facebook.com/docs/marketing-api/campaign-structure): Campaigns, AdSets, Ads, and AdCreatives. It can also sync [Ad Insights from the Reporting API](https://developers.facebook.com/docs/marketing-api/insights).

### Output schema

This Source is capable of syncing the following core Streams:

* AdSets. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign#fields)
* Ads. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/adgroup#fields)
* AdCreatives. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/ad-creative#fields)
* Campaigns. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group#fields)

The linked Facebook docs go into detail about the fields present on those streams.

In addition, this source is capable of syncing ad insights as a stream. Ad insights can also be segmented by the following categories, where each segment is synced as a separate Airbyte stream:

* Country - _coming soon_
* DMA \(Designated Market Area\) - _coming soon_
* Gender & Age - _coming soon_
* Platform & Device - _coming soon_
* Region - _coming soon_

The segmented streams contain entries of campaign/adset/ad combinations for each day broken down by the chosen segment.

For more information, see the [Facebook Insights API documentation. ](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)

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
| Incremental Sync | Yes | except AdCreatives |

### Rate Limiting & Performance Considerations

{% hint style="info" %}
Facebook heavily throttles API tokens generated from Facebook Apps by default, making it infeasible to use such a token for syncs with Airbyte. To be able to use this connector without your syncs taking days due to rate limiting follow the instructions in the Setup Guide below to access better rate limits.
{% endhint %}

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/marketing-api/overview/authorization#limits) for more information.

## Getting started

### Requirements

* A Facebook Ad Account ID  
* A Facebook App which has the Marketing API enabled
* A Facebook Marketing API Access Token
* Request a rate limit increase from Facebook

### Setup guide

### Facebook Ad Account ID

Follow the [Facebook documentation for obtaining your Ad Account ID](https://www.facebook.com/business/help/1492627900875762) and keep that on hand. We'll need this ID to configure Facebook as a source in Airbyte.

### Facebook App

#### If you don't have a Facebook App

Visit the [Facebook Developers App hub](https://developers.facebook.com/apps/) and create an App and choose "Manage Business Integrations" as the purpose of the app. Fill out the remaining fields to create your app, then follow along the "Enable the Marketing API for your app" section.

#### Enable the Marketing API for your app

From the App's Dashboard screen \(seen in the screenshot below\) enable the Marketing API for your app if it is not already setup.

![](../../.gitbook/assets/facebook_marketing_api.png)

### API Access Token

In the App Dashboard screen, click Marketing API --&gt; Tools on the left sidebar. Then highlight all the available token permissions \(`ads_management`, `ads_read`, `read_insights`\) and click "Get token". A long string of characters should appear in front of you; **this is the access token.** Copy this string for use in the Airbyte UI later.

![](../../.gitbook/assets/facebook_access_token.png)

### Request rate limit increase

Facebook [heavily throttles](https://developers.facebook.com/docs/marketing-api/overview/authorization#limits) API tokens generated from Facebook Apps with the "Standard Access" tier \(the default tier for new apps\), making it infeasible to use the token for syncs with Airbyte. You'll need to request an upgrade to Advanced Access for your app on the following permissions:

* Ads Management Standard Access
* ads\_read
* ads\_management

See the Facebook [documentation on Authorization](https://developers.facebook.com/docs/marketing-api/overview/authorization/#access-levels) for information about how to request Advanced Access to the relevant permissions.

With the Ad Account ID and API access token, you should be ready to start pulling data from the Facebook Marketing API. Head to the Airbyte UI to setup your source connector!

