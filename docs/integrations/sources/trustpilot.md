# TrustPilot

## Prerequisites

- Trustpilot API Token or Zendesk OAuth 2.0 redentials
- Trustpilot Business Unit URLs

## Setup guide

Create a Trustpilot App as described in [Trustpilot docs](https://support.trustpilot.com/hc/en-us/articles/207309867-Getting-started-with-Trustpilot-s-APIs).

Enter the API key and secret in the Airbyte source configuration "API key" and "Secret"

## Supported sync modes

The **Trustpilot** source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental Sync

## Supported Streams

This Source is capable of syncing the following Streams:

- [Configured Business Units](<https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#find-a-business-unit>) - loads business units defined in the configuration
- [Business Units](<https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#get-a-list-of-all-business-units>) - loads **all** business units
- [Private Reviews](https://documentation-apidocumentation.trustpilot.com/business-units-api#business-unit-private-reviews) \(Incremental sync\)

## Performance considerations

The connector is restricted by Trustpilot [rate limit guidelines](https://documentation-apidocumentation.trustpilot.com/#LimitRates).

The Trustpilot connector should not run into any limits under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| `1.0.0` | 2023-12-18 | [33601](https://github.com/airbytehq/airbyte/pull/33601) | Migrate to Low Code; update authentication scheme |
| `0.1.0` | 2023-03-16 | [24009](https://github.com/airbytehq/airbyte/pull/24009) | Initial version                                   |
