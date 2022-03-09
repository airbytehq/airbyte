# Twilio

## Overview

The Twilio connector can be used to sync your Twilio data. It supports full refresh sync for all streams and incremental sync for the Alerts, Calls, Conferences, Message Media, Messages, Recordings and Usage Records streams.

### Output schema

Several output streams are available from this source:

* [Accounts](https://www.twilio.com/docs/usage/api/account#read-multiple-account-resources)
* [Addresses](https://www.twilio.com/docs/usage/api/address#read-multiple-address-resources)
* [Alerts](https://www.twilio.com/docs/usage/monitor-alert#read-multiple-alert-resources) \(Incremental\)
* [Applications](https://www.twilio.com/docs/usage/api/applications#read-multiple-application-resources)
* [Available Phone Number Countries](https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-resource#read-a-list-of-countries) \(Incremental\)
* [Available Phone Numbers Local](https://www.twilio.com/docs/phone-numbers/api/availablephonenumberlocal-resource#read-multiple-availablephonenumberlocal-resources) \(Incremental\)
* [Available Phone Numbers Mobile](https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-mobile-resource#read-multiple-availablephonenumbermobile-resources) \(Incremental\)
* [Available Phone Numbers Toll Free](https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-tollfree-resource#read-multiple-availablephonenumbertollfree-resources) \(Incremental\)
* [Calls](https://www.twilio.com/docs/voice/api/call-resource#create-a-call-resource) \(Incremental\)
* [Conference Participants](https://www.twilio.com/docs/voice/api/conference-participant-resource#read-multiple-participant-resources) \(Incremental\)
* [Conferences](https://www.twilio.com/docs/voice/api/conference-resource#read-multiple-conference-resources) \(Incremental\)
* [Dependent Phone Numbers](https://www.twilio.com/docs/usage/api/address?code-sample=code-list-dependent-pns-subresources&code-language=curl&code-sdk-version=json#instance-subresources) \(Incremental\)
* [Incoming Phone Numbers](https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource#read-multiple-incomingphonenumber-resources) \(Incremental\)
* [Keys](https://www.twilio.com/docs/usage/api/keys#read-a-key-resource)
* [Message Media](https://www.twilio.com/docs/sms/api/media-resource#read-multiple-media-resources) \(Incremental\)
* [Messages](https://www.twilio.com/docs/sms/api/message-resource#read-multiple-message-resources) \(Incremental\)
* [Outgoing Caller Ids](https://www.twilio.com/docs/voice/api/outgoing-caller-ids#outgoingcallerids-list-resource)
* [Queues](https://www.twilio.com/docs/voice/api/queue-resource#read-multiple-queue-resources)
* [Recordings](https://www.twilio.com/docs/voice/api/recording#read-multiple-recording-resources) \(Incremental\)
* [Transcriptions](https://www.twilio.com/docs/voice/api/recording-transcription?code-sample=code-read-list-all-transcriptions&code-language=curl&code-sdk-version=json#read-multiple-transcription-resources)
* [Usage Records](https://www.twilio.com/docs/usage/api/usage-record#read-multiple-usagerecord-resources) \(Incremental\)
* [Usage Triggers](https://www.twilio.com/docs/usage/api/usage-trigger#read-multiple-usagetrigger-resources)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Twilio connector will gracefully handle rate limits. For more information, see [the Twilio docs for rate limitations](https://support.twilio.com/hc/en-us/articles/360044308153-Twilio-API-response-Error-429-Too-Many-Requests).

Get in touch with [Twilio Sales](https://twilio.com/help/sales) to talk to them about your use case and request an increased concurrency limit.

## Getting started

### Requirements

* Twilio Account
* Twilio Account SID and Auth Token to authenticate API requests.

### Setup guide

Twilio HTTP requests to the REST API are protected with HTTP Basic authentication. In short, you will use your Twilio Account SID as the username and your Auth Token as the password for HTTP Basic authentication.

You can find your Account SID and Auth Token on your [dashboard](https://www.twilio.com/user/account).

See [docs](https://www.twilio.com/docs/iam/api) for more details.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.2 | 2021-12-23 | [9092](https://github.com/airbytehq/airbyte/pull/9092) | Correct specification doc URL |
| 0.1.1 | 2021-10-18 | [7034](https://github.com/airbytehq/airbyte/pull/7034) | Update schemas and transform data types according to the API schema |
| 0.1.0 | 2021-07-02 | [4070](https://github.com/airbytehq/airbyte/pull/4070) | Native Twilio connector implemented |

