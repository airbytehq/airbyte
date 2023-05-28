# Kyriba

## Overview
The Kyriba source retrieves data from [Kyriba](https://kyriba.com/) using their [JSON REST APIs](https://developer.kyriba.com/apiCatalog/).

## Setup Guide

### Prerequisites

To set up the Kyriba Source connector in Airbyte, you will need the following:

- Kyriba domain
- Username
- Password

You have to reach out to Kyriba to obtain these credentials or access them from your existing account. Refer to the [Kyriba Support](https://www.kyriba.com/company/contact/).

### Step-by-Step Configuration

1. **Kyriba domain:** Enter the domain of your Kyriba instance. It should follow the pattern `subdomain.kyriba.com`. You can find this in your browser's address bar when you are logged into your Kyriba instance. The domain will look like `https://yoursubdomain.kyriba.com`, where `yoursubdomain` should be replaced with your actual subdomain.

2. **Username:** Enter your Kyriba account username that will be used for API access. This is the same username you use to log into your Kyriba account.

3. **Password:** Enter your Kyriba account password associated with the provided username. This is the same password you use to log into your Kyriba account.

4. **Start Date:** Specify the start date for the data synchronization between Airbyte and Kyriba. Enter the date in the format `YYYY-MM-DD`. This date will represent the earliest records you want to retrieve from Kyriba.

5. **End Date (optional):** Specify the end date for the data synchronization between Airbyte and Kyriba. Enter the date in the format `YYYY-MM-DD`. This date will represent the latest records you want to retrieve from Kyriba. If left empty, the sync will run up to the current date.

Once you have filled in the required fields, you can proceed to set up the connection between Airbyte and your Kyriba instance.

## Supported Streams
- [Accounts](https://developer.kyriba.com/site/global/apis/accounts/index.gsp)
- [Bank Balances](https://developer.kyriba.com/site/global/apis/bank-statement-balances/index.gsp) - End of Day and Intraday
- [Cash Balances](https://developer.kyriba.com/site/global/apis/cash-balances/index.gsp) - End of Day and Intraday 
- [Cash Flows](https://developer.kyriba.com/site/global/apis/cash-flows/index.gsp) (incremental)

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2022-07-13 | [12748](https://github.com/airbytehq/airbyte/pull/12748) | The Kyriba Source is created |
