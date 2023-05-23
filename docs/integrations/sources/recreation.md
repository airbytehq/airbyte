# Recreation.gov API

## Sync overview

**Recreation Information Database - RIDB**
RIDB is a part of the Recreation One Stop (R1S) program, which oversees the operation of Recreation.gov -- a user-friendly, web-based resource to citizens, offering a single point of access to information about recreational opportunities nationwide. The website represents an authoritative source of information and services for millions of visitors to federal lands, historic sites, museums, waterways and other activities and destinations.

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

## Getting started

### Requirements

1. A Recreation API key. You can get one by signing up [here](https://ridb.recreation.gov/).
2. Find your key by signing in to the API docs portal and clicking on your name in the top right corner.

### Setup guide

Follow the steps below to set up the Recreation Source connector with your API key:

1. If you don't already have an account, create one at [Recreation.gov](https://www.recreation.gov/) by clicking on "Sign Up" in the top right corner.
2. Go to the [API docs](https://ridb.recreation.gov/docs) portal and sign in by clicking on "Sign In" in the top right corner.
3. Click on your name or email address in the top right corner, then click on "My Account".
4. In the "My Account" section, under the "API Keys" tab, you will see your Recreation API key. If you haven't generated one yet, click on the "Generate API Key" button, then copy the generated key.
5. In the Airbyte connector configuration form for Recreation, provide the following required field:
   - `api_key`: Paste your copied Recreation API key in this field.
6. (Optional) If you want to query a specific campsite, you can provide the `query_campsites` field with the relevant campsite ID or name.

Now you are all set to use the Recreation Source connector in Airbyte.

## Changelog

| Version | Date       | Pull Request | Subject      |
|:--------|:-----------|:-------------|:-------------|
| 0.1.0   | 2022-11-02 | TBA          | First Commit |