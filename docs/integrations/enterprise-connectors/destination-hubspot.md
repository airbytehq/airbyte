---
dockerRepository: airbyte/destination-salesforce
---
# HubSpot Destination

## Overview

This page guides you through the process of setting up the [HubSpot](https://www.hubspot.com/) destination connector.

## Prerequisites

- HubSpot Account

## Setup guide

### Step 1: Set up the HubSpot connector in Airbyte

1. Log into your Airbyte account.
2. Click Destination and then click + New destination.
3. On the Set up the destination page, select HubSpot from the Destination tiles.
4. Enter a name for the HubSpot connector.
5. From the **Authentication** dropdown, OAuth authentication is available so click **Authenticate your HubSpot account** to sign in with HubSpot and authorize your account.
   
   :::note HubSpot Authentication issues
   You may encounter an error during the authentication process in the popup window with the message `An invalid scope name was provided`. To resolve this, close the window and retry authentication.
   :::

6. Click **Set up destination** and wait for the tests to complete.

## Supported Objects

The HubSpot source connector supports the following streams:

- [Companies](https://developers.hubspot.com/docs/api/crm/companies): Upsert on unique field
- [Contacts](https://developers.hubspot.com/docs/methods/contacts): Upsert on email
- [Deals](https://developers.hubspot.com/docs/api/crm/deals): Upsert on unique field
- [Custom Objects](https://developers.hubspot.com/docs/guides/api/crm/objects/custom-objects): Upsert on unique field

## Limitations & Troubleshooting

### Rate limiting

The connector is restricted by normal HubSpot [rate limitations](https://developers.hubspot.com/docs/guides/apps/api-usage/usage-details#public-apps).

### App Verification

In order to verify our HubSpot application, HubSpot expects some usage i.e. [more than 60 installations](https://developers.hubspot.com/docs/guides/apps/marketplace/certification-requirements#value). Hence, when installing the app, you might see the message "You're connecting to an unverified app". This is expected for our first users. Once we have enough traffic on the application, we will be able to verify the app which will remove this warning.

### Scopes for Unsupported Streams

During app the app installation, you might see scopes related to objects we don't support. This is expected as changing scopes might require the users to re-authenticate which is quite disruptive. In order to prevent that, we added scopes on objects we intend to support given user demands.

### 403 Forbidden Error

Hubspot has **scopes** for each API call. Each stream is tied to a scope and will need access to that scope to sync data. Review the Hubspot OAuth scope documentation [here](https://developers.hubspot.com/docs/api/working-with-oauth#scopes).