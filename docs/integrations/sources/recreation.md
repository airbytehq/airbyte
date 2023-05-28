# Recreation.gov API

## Sync overview

**Recreation Information Database - RIDB**
RIDB is a part of the Recreation One Stop (R1S) program, 
which oversees the operation of Recreation.gov -- a user-friendly, web-based 
resource to citizens, offering a single point of access to information about 
recreational opportunities nationwide. The website represents an authoritative 
source of information and services for millions of visitors to federal lands, 
historic sites, museums, waterways and other activities and destinations.

This source retrieves data from the [Recreation API](https://ridb.recreation.gov/landing).
### Output schema

This source is capable of syncing the following streams:

* Activities
* Campsites
* Events
* Facilities
* Facility Addresses
* Links
* Media
* Organizations
* Permit Entrances
* Recreation Areas
* Recreation Area Addresses
* Tours

### Features

| Feature           | Supported? \(Yes/No\) | Notes |
|:------------------|:----------------------|:------|
| Full Refresh Sync | Yes                   |       |
| Incremental Sync  | No                    |       |

### Performance considerations

The Recreation API has a rate limit of 50 requests per minute.

## Setup Guide

In this guide, you will learn how to set up the Recreation Source connector in Airbyte. This involves obtaining an API key from the Recreation website, and configuring the connector with the necessary information.

### Prerequisites

To set up the Recreation Source connector, you need to have an Recreation API key. If you do not have one yet, you can obtain it by following these steps:

1. Sign up for an account on the Recreation website by visiting [https://www.recreation.gov/](https://www.recreation.gov/) and clicking on "Sign In / Sign Up" at the top right corner of the page.
2. After signing up, sign in to your account.
3. Navigate to the [API documentation portal](https://ridb.recreation.gov/).
4. Click on “Get API Key” to request an API key. Your API key will be sent to the email address you provided during the sign-up process.

Once you have the API key, you can proceed with the connector configuration.

### Configuring the Connector

To configure the Recreation Source connector in Airbyte, you need to provide the API key you obtained in the previous step. Here is a step-by-step guide:

1. In the Airbyte UI, locate the "Create Source" form.
2. Fill in the required fields as follows:
   * `apikey`: Enter your Recreation API key obtained in the previous step.
   * `query_campsites`: (Optional) Enter a search query if you want to filter campsites.
3. Click on the "Set up Source" button to save and validate your configuration.

After configuring the connector, Airbyte will use the provided API key to access and synchronize data from the Recreation API.

For further information on the Recreation API, refer to their official [documentation](https://ridb.recreation.gov/public/apis/docs).

## Changelog

| Version | Date       | Pull Request | Subject      |
|:--------|:-----------|:-------------|:-------------|
| 0.1.0   | 2022-11-02 | TBA          | First Commit |