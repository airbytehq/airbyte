# Partnerstack

Airbyte destination connector for Partnerstack.


## Sync overview

Currently only `append` is supported.

Conventions:

- The `message` data will be mapped one by one to the table schema.
The data must have the same columns, mapping the names and data types, according the endpoint you choose.

## Getting Started

In order to connect, you need:
* API Keys: 
  * **Public Key** 
  * **Private Key**

See [this](https://docs.partnerstack.com/reference/auth) to get your API Keys


* **Endpoint**

See [this](https://docs.partnerstack.com/reference/base-url) to know all available endpoints with Partnerstack API

Example : *to create transactions -> set `transactions` as endpoint*



## CHANGELOG

| Version | Date       | Pull Request                                           | Subject                         |
| :------ | :--------- | :----------------------------------------------------- | :------------------------------ |
| 0.1.0   | 2023-07-21 | [XXXX](https://github.com/airbytehq/airbyte/pull/XXXX) | 🎉 New Destination: Partnerstack |

