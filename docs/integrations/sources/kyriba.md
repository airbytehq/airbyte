# Kyriba

## Overview
The Kyriba source retrieves data from [Kyriba](https://kyriba.com/) using their [JSON REST APIs](https://developer.kyriba.com/apiCatalog/).

## Setup Guide

### Requirements
- Kyriba domain
- Username 
- Password

### Obtain the required information from Kyriba

To obtain the Kyriba domain, username, and password, follow these steps:

1. Log in to your Kyriba account at [https://signin.kyriba.com/login](https://signin.kyriba.com/login).

2. Click on your username in the top-right corner and select **Profile** from the drop-down menu.

3. Under the **API Access** section, take note of the following:
   - Kyriba Domain: This is the URL used to access your Kyriba account. For example, `demo.kyriba.com`.
   - Username: Your Kyriba account's username, used for API authentication.
   - Password: Your Kyriba account's password, used for API authentication.

If you still have difficulty obtaining the required information, you can reach out to Kyriba support by creating a ticket in the [Kyriba Client support portal](https://login.kyriba.com/kyribaservice/login.asp).

### Configure the Kyriba Source in Airbyte

Once you have obtained the required information from Kyriba, enter it into the Airbyte Connector configuration form:

- **Domain**: Enter the Kyriba domain you obtained in the API Access section of your Kyriba profile.
- **Username**: Enter the Kyriba username you obtained in the API Access section of your Kyriba profile.
- **Password**: Enter the Kyriba password you obtained in the API Access section of your Kyriba profile.
- **Start Date**: Enter the date the sync should start from, in the format `YYYY-MM-DD`. For example, `2021-01-10`.
- **End Date**: (Optional) Enter the date the sync should end. If left empty, the sync will run up to the current date. The format is `YYYY-MM-DD`. For example, `2022-03-01`.

## Supported Streams
- [Accounts](https://developer.kyriba.com/site/global/apis/accounts/index.gsp)
- [Bank Balances](https://developer.kyriba.com/site/global/apis/bank-statement-balances/index.gsp) - End of Day and Intraday
- [Cash Balances](https://developer.kyriba.com/site/global/apis/cash-balances/index.gsp) - End of Day and Intraday 
- [Cash Flows](https://developer.kyriba.com/site/global/apis/cash-flows/index.gsp) (incremental)

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2022-07-13 | [12748](https://github.com/airbytehq/airbyte/pull/12748) | The Kyriba Source is created |