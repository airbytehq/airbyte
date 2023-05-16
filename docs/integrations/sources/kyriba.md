# Kyriba

## Overview
The Kyriba source retrieves data from [Kyriba](https://kyriba.com/) using their [JSON REST APIs](https://developer.kyriba.com/apiCatalog/).

## Set Up Guide

### Prerequisites
To configure the Kyriba source connector, you need the following information from Kyriba:
- Kyriba domain
- Username
- Password

If you don't have a Kyriba account or the above information, contact [Kyriba Support](https://www.kyriba.com/support/) to get your account set up.

### Create a New Connection
Follow these steps to configure the Kyriba source connector in Airbyte:

1. In Airbyte, navigate to the Connections page and click the "Create new connection" button.
2. Select "Kyriba" from the list of sources.
3. In the Configuration screen, provide the following details:
   - **Domain:** Your Kyriba domain name, for example `demo.kyriba.com`.
   - **Username:** Your Kyriba username.
   - **Password:** Your Kyriba password.
   - **Start Date:** The date that the sync should start from, in the format `YYYY-MM-DD`. This field is required.
   - **End Date:** The date that the sync should end. If left empty, the sync will run to the current date. This field is optional.

   ![Kyriba Configuration](https://airbyte-public-assets.s3.amazonaws.com/documentation/sources/kyriba/01-kyriba-configuration.png)

4. Click the "Check connection" button to verify the provided details are correct. If the verification fails, double-check the provided details and make sure they are correct.
5. If the verification passes, click the "Create" button to create the connection.

### Supported Streams
The Kyriba source supports the following streams:
- [Accounts](https://developer.kyriba.com/site/global/apis/accounts/index.gsp)
- [Bank Balances](https://developer.kyriba.com/site/global/apis/bank-statement-balances/index.gsp) - End of Day and Intraday
- [Cash Balances](https://developer.kyriba.com/site/global/apis/cash-balances/index.gsp) - End of Day and Intraday
- [Cash Flows](https://developer.kyriba.com/site/global/apis/cash-flows/index.gsp) (incremental)

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2022-07-13 | [12748](https://github.com/airbytehq/airbyte/pull/12748) | The Kyriba Source is created |