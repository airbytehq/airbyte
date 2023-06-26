# Twilio

This page contains the setup guide and reference information for the Twilio source connector.

## Prerequisites

Twilio HTTP requests to the REST API are protected with HTTP Basic authentication. In short, you will use your Twilio Account SID as the username and your Auth Token as the password for HTTP Basic authentication.

You can find your Account SID and Auth Token on your [dashboard](https://www.twilio.com/user/account).

See [docs](https://www.twilio.com/docs/iam/api) for more details.

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Twilio connector and select **Twilio** from the <Source/Destination> type dropdown.
4. Enter your `account_sid`.
5. Enter your `auth_token`.
6. Enter your `start_date`.
7. Enter your `lookback_window`.
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `account_sid`.
4. Enter your `auth_token`.
5. Enter your `start_date`.
6. Enter your `lookback_window`.
7. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Twilio source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

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
* [Conversations](https://www.twilio.com/docs/conversations/api/conversation-resource#read-multiple-conversation-resources) 
* [Conversation Messages](https://www.twilio.com/docs/conversations/api/conversation-message-resource#list-all-conversation-messages)
* [Conversation Participants](https://www.twilio.com/docs/conversations/api/conversation-participant-resource)
* [Dependent Phone Numbers](https://www.twilio.com/docs/usage/api/address?code-sample=code-list-dependent-pns-subresources&code-language=curl&code-sdk-version=json#instance-subresources) \(Incremental\)
* [Executions](https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource#read-multiple-incomingphonenumber-resources) \(Incremental\)
* [Incoming Phone Numbers](https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource#read-multiple-incomingphonenumber-resources) \(Incremental\)
* [Flows](https://www.twilio.com/docs/studio/rest-api/flow#read-a-list-of-flows)
* [Keys](https://www.twilio.com/docs/usage/api/keys#read-a-key-resource)
* [Message Media](https://www.twilio.com/docs/sms/api/media-resource#read-multiple-media-resources) \(Incremental\)
* [Messages](https://www.twilio.com/docs/sms/api/message-resource#read-multiple-message-resources) \(Incremental\)
* [Outgoing Caller Ids](https://www.twilio.com/docs/voice/api/outgoing-caller-ids#outgoingcallerids-list-resource)
* [Queues](https://www.twilio.com/docs/voice/api/queue-resource#read-multiple-queue-resources)
* [Recordings](https://www.twilio.com/docs/voice/api/recording#read-multiple-recording-resources) \(Incremental\)
* [Services](https://www.twilio.com/docs/chat/rest/service-resource#read-multiple-service-resources)
* [Roles](https://www.twilio.com/docs/chat/rest/role-resource#read-multiple-role-resources)
* [Transcriptions](https://www.twilio.com/docs/voice/api/recording-transcription?code-sample=code-read-list-all-transcriptions&code-language=curl&code-sdk-version=json#read-multiple-transcription-resources)
* [Trunks](https://www.twilio.com/docs/sip-trunking/api/trunk-resource#trunk-properties)
* [Usage Records](https://www.twilio.com/docs/usage/api/usage-record#read-multiple-usagerecord-resources) \(Incremental\)
* [Usage Triggers](https://www.twilio.com/docs/usage/api/usage-trigger#read-multiple-usagetrigger-resources)

## Performance considerations

The Twilio connector will gracefully handle rate limits.
For more information, see [the Twilio docs for rate limitations](https://support.twilio.com/hc/en-us/articles/360044308153-Twilio-API-response-Error-429-Too-Many-Requests-).

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                                                                 |
|:--------|:-----------|:----------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
| 0.7.0   | 2023-05-03 | [25781](https://github.com/airbytehq/airbyte/pull/25781)      | Add new stream `Trunks`                                                              |
| 0.6.0   | 2023-05-03 | [](https://github.com/airbytehq/airbyte/pull/)      | Add new stream `Roles` with parent `Services`                                                              |
| 0.5.0   | 2023-03-21 | [23995](https://github.com/airbytehq/airbyte/pull/23995)  | Add new stream `Conversation Participants`                                                              |
| 0.4.0   | 2023-03-18 | [23995](https://github.com/airbytehq/airbyte/pull/23995)  | Add new stream `Conversation Messages`                                                                  |
| 0.3.0   | 2023-03-18 | [22874](https://github.com/airbytehq/airbyte/pull/22874)  | Add new stream `Executions` with parent `Flows`                                                         |
| 0.2.0   | 2023-03-16 | [24114](https://github.com/airbytehq/airbyte/pull/24114)  | Add `Conversations` stream                                                                              |
| 0.1.16  | 2023-02-10 | [22825](https://github.com/airbytehq/airbyte/pull/22825)  | Specified date formatting in specification                                                              |
| 0.1.15  | 2023-01-27 | [22025](https://github.com/airbytehq/airbyte/pull/22025)  | Set `AvailabilityStrategy` for streams explicitly to `None`                                             |
| 0.1.14  | 2022-11-16 | [19479](https://github.com/airbytehq/airbyte/pull/19479)  | Fix date range slicing                                                                                  |
| 0.1.13  | 2022-10-25 | [18423](https://github.com/airbytehq/airbyte/pull/18423)  | Implement datetime slicing for streams supporting incremental syncs                                     |
| 0.1.11  | 2022-09-30 | [17478](https://github.com/airbytehq/airbyte/pull/17478)  | Add lookback_window parameters                                                                          |
| 0.1.10  | 2022-09-29 | [17410](https://github.com/airbytehq/airbyte/pull/17410)  | Migrate to per-stream states                                                                            |
| 0.1.9   | 2022-09-26 | [17134](https://github.com/airbytehq/airbyte/pull/17134)  | Add test data for Message Media and Conferences                                                         |
| 0.1.8   | 2022-08-29 | [16110](https://github.com/airbytehq/airbyte/pull/16110)  | Add state checkpoint interval                                                                           |
| 0.1.7   | 2022-08-26 | [15972](https://github.com/airbytehq/airbyte/pull/15972)  | Shift start date for stream if it exceeds 400 days                                                      |
| 0.1.6   | 2022-06-22 | [14000](https://github.com/airbytehq/airbyte/pull/14000)  | Update Records stream schema and align tests with connectors' best practices                            |
| 0.1.5   | 2022-06-22 | [13896](https://github.com/airbytehq/airbyte/pull/13896)  | Add lookback window parameters to fetch messages with a rolling window and catch status updates         |
| 0.1.4   | 2022-04-22 | [12157](https://github.com/airbytehq/airbyte/pull/12157)  | Use Retry-After header for backoff                                                                      |
| 0.1.3   | 2022-04-20 | [12183](https://github.com/airbytehq/airbyte/pull/12183)  | Add new subresource on the call stream + declare a valid primary key for conference_participants stream |
| 0.1.2   | 2021-12-23 | [9092](https://github.com/airbytehq/airbyte/pull/9092)    | Correct specification doc URL                                                                           |
| 0.1.1   | 2021-10-18 | [7034](https://github.com/airbytehq/airbyte/pull/7034)    | Update schemas and transform data types according to the API schema                                     |
| 0.1.0   | 2021-07-02 | [4070](https://github.com/airbytehq/airbyte/pull/4070)    | Native Twilio connector implemented                                                                     |
