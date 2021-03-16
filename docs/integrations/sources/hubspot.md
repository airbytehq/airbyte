# Hubspot

## Overview

The Hubspot connector can be used to sync your Hubspot data. It supports full refresh sync for all streams and incremental sync for Email Events and Subscription Changes streams. 

### Output schema

Several output streams are available from this source:
* [Campaigns](https://developers.hubspot.com/docs/methods/email/get_campaign_data)
* [Companies](https://developers.hubspot.com/docs/api/crm/companies)
* [Contact Lists](http://developers.hubspot.com/docs/methods/lists/get_lists)
* [Contacts](https://developers.hubspot.com/docs/methods/contacts/get_contacts)
* [Deal Pipelines](https://developers.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type)
* [Deals](https://developers.hubspot.com/docs/api/crm/deals)
* [Email Events](https://developers.hubspot.com/docs/methods/email/get_events) (Incremental)
* [Engagements](https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements)
* [Forms](https://developers.hubspot.com/docs/api/marketing/forms)
* [Line Items](https://developers.hubspot.com/docs/api/crm/line-items)
* [Owners](https://developers.hubspot.com/docs/methods/owners/get_owners)
* [Products](https://developers.hubspot.com/docs/api/crm/products)
* [Quotes](https://developers.hubspot.com/docs/api/crm/quotes)
* [Subscription Changes](https://developers.hubspot.com/docs/methods/email/get_subscriptions_timeline) (Incremental)
* [Tickets](https://developers.hubspot.com/docs/api/crm/tickets)
* [Workflows](https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The connector is restricted by normal Hubspot [rate limitations](https://legacydocs.hubspot.com/apps/api_guidelines).

## Getting started

### Requirements

* Hubspot Account
* Api credentials

### Setup guide

This connector supports only authentication with API Key.
To obtain API key for the account go to settings -&gt; integrations \(under the account banner\) -&gt; api key. 
If you already have an api key you can use that. Otherwise generated a new one.
See [docs](https://knowledge.hubspot.com/integrations/how-do-i-get-my-hubspot-api-key) for more details.
