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
| Full Refresh Sync  | Yes                   |       |
| Incremental Sync   | No                    |       |

### Performance considerations

The Recreation API has a rate limit of 50 requests per minute.

## Getting started

### Requirements

1. A Recreation API key. You can get one by signing up [here](https://www.recreation.gov/).
2. Find your key by signing in to the API docs portal and clicking on your name in the top right corner.

### Setup guide

To set up the Recreation Source connector in Airbyte, follow these steps:

1. In the **Airbyte UI**, navigate to the **Recreation Source** connector configuration page.
2. Input the following fields in the configuration form:

- `api_key`: Your Recreation API key.

3. Click **Test Connection** to confirm that the API key has been authorized.
4. Once the connection is successful, click **Create** to save the configuration.
5. You are now ready to sync data from the Recreation API.

For more information on the Recreation API, see the [documentation](https://ridb.recreation.gov/landing).