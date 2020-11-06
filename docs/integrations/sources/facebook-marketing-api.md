# Facebook Marketing API

## Sync overview

This source can sync data for the core Ad Campaign data available[ in the Facebook Marketing API](https://developers.facebook.com/docs/marketing-api/campaign-structure): Campaigns, AdSets, Ads, and AdCreatives. It can also sync [Ad Insights from the Reporting API](https://developers.facebook.com/docs/marketing-api/insights).

This Source Connector is based on the [Singer Facebook Tap](https://github.com/singer-io/tap-facebook).

### Output schema

This Source is capable of syncing the following core Streams:

* AdSets. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign#fields)
* Ads. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/adgroup#fields)
* AdCreatives. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/ad-creative#fields)
* Campaigns. [Facebook docs](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group#fields)

The linked Facebook docs go into detail about the fields present on those streams.

In addition, this source is capable of syncing ad insights as a stream. Ad insights can also be segmented by the following categories, where each segment is synced as a separate Airbyte stream:

* Country
* DMA \(Designated Market Area\)
* Gender & Age
* Platform & Device
* Region

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
| Full Refresh Sync | yes |  |
| Incremental Sync | no |  |

### Performance considerations

**Important note:** In order for data synced from your Facebook account to be up to date, you might need to apply with Facebook to upgrade your access token to the Ads Management Standard Tier as specified in the [Facebook Access documentation](https://developers.facebook.com/docs/marketing-api/access). Otherwise, Facebook might throttle Airbyte syncs, since the default tier \(Dev Access\) is heavily throttled by Facebook.

Note that Airbyte can adapt to throttling from Facebook. In the worst case scenario syncs from Facebook will take longer to complete and data will be less fresh.

## Getting started

### Requirements

* A Facebook Ad Account ID  
* A Facebook App which has the Marketing API enabled
* A Facebook Marketing API Access Token

### Setup guide

### Facebook Ad Account ID

Follow the [Facebook documentation for obtaining your Ad Account ID](https://www.facebook.com/business/help/1492627900875762) and keep that on hand. We'll need this ID to configure Facebook as a source in Airbyte.

### Facebook App

#### If you don't have a Facebook App

Visit the [Facebook Developers App hub](https://developers.facebook.com/apps/) and create an App and choose "Manage Business Integrations" as the purpose of the app. Fill out the remaining fields to create your app, then follow along the "Enable the Marketing API for your app" section.

#### Enable the Marketing API for your app

From the App's Dashboard screen \(seen in the screenshot below\) enable the Marketing API for your app if it is not already setup.

![](../../.gitbook/assets/screen-shot-2020-11-03-at-9.25.21-pm%20%281%29%20%281%29.png)

### API Access Token

In the App Dashboard screen, click Marketing API --&gt; Tools on the left sidebar. Then highlight all the available token permissions \(`ads_management`, `ads_read`, `read_insights`\) and click "Get token". A long string of characters should appear in front of you; **this is the access token.** Copy this string for use in the Airbyte UI later.

![](../../.gitbook/assets/screen-shot-2020-11-03-at-9.35.40-pm%20%281%29%20%281%29.png)

With the Ad Account ID and API access token, you should be ready to start pulling data from the Facebook Marketing API. Head to the Airbyte UI to setup your source connector!

