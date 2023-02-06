# Yandex Metrica

This page guides you through the process of setting up the Yandex Metrica source connector.

## Prerequisites

- Counter ID
- OAuth2 Token

## Setup Yandex Metrica

1. [Create a Yandex Metrica account](https://metrica.yandex.com/) if you don't already have one.
2. Head to [Management page](https://metrica.yandex.com/list) and add new tag or choose an existing one.
3. At the top of the dasboard you will see 8 digit number to the right of your website name. This is your **Counter ID**.
4. Create a new app or choose an existing one from [My apps page](https://oauth.yandex.com/).
   - Which platform is the app required for?: **Web services**
   - Callback URL: https://oauth.yandex.com/verification_code
   - What data do you need?: **Yandex.Metrica**. Read permission will suffice.
5. Choose your app from [the list](https://oauth.yandex.com/).
   - To create your API key you will need to grab your **ClientID**,
   - Now to get the API key craft a GET request to an endpoint *https://oauth.yandex.com/authorizE?response_type=token&client_id=\<Your Client ID\>*
   - You will receive a response with your **API key**. Save it.

## Supported sync modes

The Yandex Metrica source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental
  - After the first sync the connector will set the state for next sync. The **start date** will be set to last syncs **end date**. The **end date** will be set to 1 day before today.

## Supported Streams

- [Views](https://yandex.com/dev/metrika/doc/api2/logs/fields/hits.html) (Incremental).
- [Sessions](https://yandex.com/dev/metrika/doc/api2/logs/fields/visits.html) (Incremental).

## Notes

- We recommend syncing data once a day. Because of the Yandex Metrica API limitation it is only possible to extract records up to yesterdays date. Todays records will only be available tomorrow.
- Because of the way API works some syncs may take a long time to finish. Timeout period is 2 hours.

## Changelog

| Version | Date       | Pull Request                                             | Subject                       |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------- |
| 0.1.0   | 2022-09-09 | [15061](https://github.com/airbytehq/airbyte/pull/15061) | 🎉 New Source: Yandex metrica |
