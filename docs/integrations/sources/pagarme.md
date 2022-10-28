# Pagar.me

Pagar.me is a financial solution for vendors, and part of the Stone group. They develop a payment processor system, providing a full payment service for merchants who want to accept payments online.

## Prerequisites
* A Pagar.me account
* `api_key` credential. Can be found on the Dashboard. For more information, consult Pagar.me [documentation](https://docs.pagar.me/v1/reference/principios-basicos#autentica%C3%A7%C3%A3o).

## Airbyte Open Source
* Start Date
* API Key

## Supported sync modes

The RD Station Marketing source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental

## Supported Streams

* Balance
* Bank Accounts
* Cards
* Chargebacks
* Customers
* Payables
* Payment Links
* Plans
* Recipients
* Refunds
* Security Rules
* Transactions
* Transfers

## Performance considerations

There is no clear performance limitation.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                         |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------- |
| 0.1.0   | 2022-10-28 | [18348](https://github.com/airbytehq/airbyte/pull/18622)  | Initial Release 