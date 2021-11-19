# Airtable

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

This source syncs data from the [Airtable API](https://airtable.com/api).

## Supported Tables

This source allows you to configure any table in your Airtable base. In case you you rename or add a column to any existing table, you will need to recreate the source to update the Airbyte catalog. 

## Getting started

**Requirements**

* api_key
* base_id
* tables 

**Setup guide**

Information about how to get credentials you may find [here](https://support.airtable.com/hc/en-us/articles/219046777-How-do-I-get-my-API-key-).

### Performance Considerations (Airbyte Open-Source)

Information about rate limits you may find [here](https://support.airtable.com/hc/en-us/articles/203313985-Public-REST-API).


## CHANGELOG