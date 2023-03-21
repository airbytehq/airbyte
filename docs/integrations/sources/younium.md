# Younium

This page contains the setup guide and reference information for the Younium source connector.

## Prerequisites

This Younium source uses the [Younium API](https://developer.younium.com/).

## Setup guide

### Step 1: Set up Younium

#### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Enter a name for your source
3. Enter your Younium `username`
4. Enter your Younium `password`
5. Enter your Younium `legal_entity`. You can find the legal entity name in your account setting if you log in to the [Younium web platform](https://app.younium.com/)
6. Click **Set up source**

## Supported sync modes

The Younium source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- [Subscriptions](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Subscriptions)
- [Products](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Products)
- [Invoices](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Invoices)

## Changelog

| Version | Date       | Pull Request                                             | Subject                             |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------- |
| 0.1.0   | 2022-11-09 | [18758](https://github.com/airbytehq/airbyte/pull/18758) | 🎉 New Source: Younium [python cdk] |
