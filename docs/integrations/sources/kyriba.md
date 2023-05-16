# Kyriba

## Overview
The Kyriba source retrieves data from [Kyriba](https://kyriba.com/) using their [JSON REST APIs](https://developer.kyriba.com/apiCatalog/).

## Setup Guide

To set up the Kyriba source connector, please follow the steps below:

### Prerequisites
- Kyriba domain
- Username 
- Password

To retrieve these details, please contact Kyriba support.

### Step 1 - Create a Kyriba API User
To extract data from Kyriba, you will need to create a new API user on your Kyriba account. Please follow the instructions in [Kyriba's documentation](https://help.kyriba.com/Developers/API) to create a new user and assign them the **API Data Access** role.

### Step 2 - Configure Kyriba Source in Airbyte
In the Airbyte connector configuration form, fill in the following details from your Kyriba API user:

- **Domain**: The Kyriba domain where your account is hosted. Example: "demo.kyriba.com".
- **Username**: The API user created in Step 1.
- **Password**: The API user password.
- **Start Date**: The date the sync should start from. Format: YYYY-MM-DD.
- **End Date** (optional): The date the sync should end. If left empty, the sync will run until the current date.

### Supported Streams
The Kyriba source connector for Airbyte supports the following streams:

- [Accounts](https://developer.kyriba.com/site/global/apis/accounts/index.gsp)
- [Bank Balances](https://developer.kyriba.com/site/global/apis/bank-statement-balances/index.gsp) - End of Day and Intraday
- [Cash Balances](https://developer.kyriba.com/site/global/apis/cash-balances/index.gsp) - End of Day and Intraday 
- [Cash Flows](https://developer.kyriba.com/site/global/apis/cash-flows/index.gsp) (incremental)

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2022-07-13 | [12748](https://github.com/airbytehq/airbyte/pull/12748) | The Kyriba Source is created |