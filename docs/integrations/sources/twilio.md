# Twilio

## Overview

The Twilio source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Twilio API](https://www.twilio.com/docs/usage/api).

This Source Connector is based on a [Singer Tap](https://github.com/transferwise/pipelinewise-tap-twilio).

### Output schema

This Source is capable of syncing the following core Streams:

* [Accounts](https://www.twilio.com/docs/usage/api/account#read-multiple-account-resources)
* [Addresses](https://www.twilio.com/docs/usage/api/address#read-multiple-address-resources)
* [Dependent phone numbers](https://www.twilio.com/docs/usage/api/address?code-sample=code-list-dependent-pns-subresources&code-language=curl&code-sdk-version=json#instance-subresources)
* [Applications](https://www.twilio.com/docs/usage/api/applications#read-multiple-application-resources)
* [Available phone number countries](https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-resource#read-a-list-of-countries)
* [Available phone numbers local](https://www.twilio.com/docs/phone-numbers/api/availablephonenumberlocal-resource#read-multiple-availablephonenumberlocal-resources)
* [Available phone numbers mobile](https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-mobile-resource#read-multiple-availablephonenumbermobile-resources)
* [Available phone numbers toll free](https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-tollfree-resource#read-multiple-availablephonenumbertollfree-resources)
* [Incoming phone numbers](https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource#read-multiple-incomingphonenumber-resources)
* [Keys](https://www.twilio.com/docs/usage/api/keys#read-a-key-resource)
* [Calls](https://www.twilio.com/docs/sms/api/message-resource#read-multiple-message-resources)
* [Conferences](https://www.twilio.com/docs/voice/api/conference-resource#read-multiple-conference-resources)
* [Conference participants](https://www.twilio.com/docs/voice/api/conference-participant-resource#read-multiple-participant-resources)
* [Outgoing caller IDs](https://www.twilio.com/docs/voice/api/outgoing-caller-ids#outgoingcallerids-list-resource)
* [Recordings](https://www.twilio.com/docs/voice/api/recording#read-multiple-recording-resources)
* [Transcriptions](https://www.twilio.com/docs/voice/api/recording-transcription?code-sample=code-read-list-all-transcriptions&code-language=curl&code-sdk-version=json#read-multiple-transcription-resources)
* [Queues](https://www.twilio.com/docs/voice/api/queue-resource#read-multiple-queue-resources)
* [Message media](https://www.twilio.com/docs/sms/api/media-resource#read-multiple-media-resources)
* [Messages](https://www.twilio.com/docs/sms/api/message-resource#read-multiple-message-resources) 
  (stream data can only be received for the last 400 days)
* [Usage records](https://www.twilio.com/docs/usage/api/usage-record#read-multiple-usagerecord-resources)
* [Usage triggers](https://www.twilio.com/docs/usage/api/usage-trigger#read-multiple-usagetrigger-resources)
* [Alerts](https://www.twilio.com/docs/usage/monitor-alert#read-multiple-alert-resources)

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
| Incremental - Append Sync | Yes |  |

### Performance considerations

The Twilio connector should not run into Twilio API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Twilio Account ID 
* Twilio access token 
* API User Email for Twilio Account

### Setup guide

Generate a API access token using the [Twilio documentation](https://support.twilio.com/hc/en-us/articles/223136027-Auth-Tokens-and-How-to-Change-Them)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

