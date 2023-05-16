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
The following instructions outline how to set up the Recreation Source Connector with Airbyte.

### Requirements
1. A Recreation API key. If you do not have one, sign up [here](https://www.recreation.gov/).
2. Access to the API docs portal.

### Setup guide
1. In the Airbyte UI, navigate to the Configuration Form for the Recreation Source Connector.
2. Fill out the section titled `Recreation Spec`.
   * In the `apikey` field, paste in your Recreation API key. This is a required field.
   * (Optional) In the `query_campsites` field, enter any additional parameters you would like to pass in the API request.
3. Once you have entered your API key, select `Save` to save the configuration.
4. Test the connection to ensure that everything is working as expected.

### Notes
* The `apikey` field is required for the Recreation Source Connector to work.
* The `query_campsites` field is optional and can be used to pass in any additional parameters you would like in the API request. 
* You can find your Recreation API key by signing into the API docs portal and clicking on your name in the top right corner.
* The Recreation API has a rate limit of 50 requests per minute, so keep this in mind when syncing data.

## Changelog

| Version | Date       | Pull Request | Subject      |
|:--------|:-----------|:-------------|:-------------|
| 0.1.0   | 2022-11-02 | TBA          | First Commit |