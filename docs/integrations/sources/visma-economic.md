# Visma e-conomic

## Sync overview

This source collects data from [Visma e-conomic](https://developer.visma.com/api/e-conomic/).
At the moment the source only implements full refresh, meaning you will sync all records with every new sync.

## Prerequisites

- Your Visma e-conomic Agreement Grant Token
- Your Visma e-conomic App Secret Token

[This page](https://www.e-conomic.com/developer/connect) guides you through the different ways of connecting to the api.
In sort your options are:

- Developer agreement
- Create a free [sandbox account](https://www.e-conomic.dk/regnskabsprogram/demo-alle), valid for 14 days.
- Demo tokens: `app_secret_token=demo` and `agreement_grant_token=demo`

## Set up the Visma e-conomic source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Stripe** from the Source type dropdown.
4. Enter a name for your source.
5. Enter **Agreement Grant Token**.
6. Enter **Secret Key**.

## This Source Supports the Following Streams

- [accounts](https://restdocs.e-conomic.com/#get-accounts)
- [customers](https://restdocs.e-conomic.com/#get-customers)
- [invoices booked](https://restdocs.e-conomic.com/#get-invoices-booked)
- [invoices booked document](https://restdocs.e-conomic.com/#get-invoices-booked-bookedinvoicenumber)
- [invoices paid](https://restdocs.e-conomic.com/#get-invoices-paid)
- [invoices total](https://restdocs.e-conomic.com/#get-invoices-totals)
- [products](https://restdocs.e-conomic.com/#get-products)

For more information about the api see the [E-conomic REST API Documentation](https://restdocs.e-conomic.com/#tl-dr).

### [Sync models](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes)

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.4   | 2024-04-19 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | Updating to 0.80.0 CDK                                                          |
| 0.2.3   | 2024-04-18 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | Manage dependencies with Poetry.                                                |
| 0.2.2   | 2024-04-15 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1   | 2024-04-12 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | schema descriptions                                                             |
| 0.2.0   | 2023-10-20 | [30991](https://github.com/airbytehq/airbyte/pull/30991) | Migrate to Low-code Framework                                                   |
| 0.1.0   | 2022-11-08 | [18595](https://github.com/airbytehq/airbyte/pull/18595) | Adding Visma e-conomic as a source                                              |
