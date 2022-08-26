# Marketo

## Sync overview

The Marketo source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This connector is based on the [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This connector can be used to sync the following tables from Marketo:

* **activities\_X** where X is an activity type contains information about lead activities of the type X. For example, activities\_send\_email contains information about lead activities related to the activity type `send_email`. See the [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getLeadActivitiesUsingGET) for a detailed explanation of what each column means. 
* **activity\_types.** Contains metadata about activity types. See the [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getAllActivityTypesUsingGET) for a detailed explanation of columns. 
* **campaigns.** Contains info about your Marketo campaigns. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Campaigns/getCampaignsUsingGET). 
* **leads.** Contains info about your Marketo leads. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Leads/getLeadByIdUsingGET). 
* **lists.** Contains info about your Marketo static lists. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Static_Lists/getListByIdUsingGET). 
* **programs.** Contins info about your Marketo programs. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Programs/browseProgramsUsingGET). 

### Data type mapping

| Integration Type | Airbyte Type | Notes                                                                           |
|:-----------------|:-------------|:--------------------------------------------------------------------------------|
| `array`          | `array`      | primitive arrays are converted into arrays of the types described in this table |
| `int`, `long`    | `number`     |                                                                                 |
| `object`         | `object`     |                                                                                 |
| `string`         | `string`     | \`\`                                                                            |
| Namespaces       | No           |                                                                                 |

### Features

Feature

| Supported?\(Yes/No\)      | Notes |
|:--------------------------|:------|
| Full Refresh Sync         | Yes   |
| Incremental - Append Sync | Yes   |

### Performance considerations

By default, Marketo caps all accounts to 50,000 API calls per day.

By default, this connector caps itself to 40,000 API calls per day. But you can also customize the maximum number of API calls this source connector makes per day to Marketo \(which may be helpful if you have for example other applications which are also hitting the Marketo API\). If this source connector reaches the maximum number you configured, it will not replicate any data until the next day.

If the 50,000 limit is too stringent, contact Marketo support for a quota increase.

## Getting started

### Requirements

* \(Optional\) Whitelist Airbyte's IP address if needed
* An API-only Marketo User Role 
* An Airbyte Marketo API-only user
* A Marketo API Custom Service
* Marketo Client ID & Client Secret
* Marketo Base URL 

### Setup guide

**Step 1: \(Optional\) whitelist Airbyte's IP address**

If you don't have IP Restriction enabled in Marketo, skip this step.

If you have IP Restriction enabled in Marketo, you'll need to whitelist the IP address of the machine running your Airbyte instance. To obtain your IP address, run `curl ifconfig.io` from the node running Airbyte. You might need to enlist an engineer to help with this. Copy the IP address returned and keep it on hand.

Once you have the IP address, whitelist it by following the Marketo documentation for [allowlisting IP addresses](https://docs.marketo.com/display/public/DOCS/Create+an+Allowlist+for+IP-Based+API+Access) for API based access.

#### Step 2: Create an API-only Marketo User Role

Follow the [Marketo documentation for creating an API-only Marketo User Role](https://docs.marketo.com/display/public/DOCS/Create+an+API+Only+User+Role).

#### Step 3: Create an Airbyte Marketo API-only user

Follow the [Marketo documentation to create an API only user](https://docs.marketo.com/display/public/DOCS/Create+an+API+Only+User)

**Step 4: Create a Marketo API custom service**

Follow the [Marketo documentation for creating a custom service for use with a REST API](https://docs.marketo.com/display/public/DOCS/Create+a+Custom+Service+for+Use+with+ReST+API).

Make sure to follow the "**Credentials for API Access"** section in the Marketo docs to generate a **Client ID** and **Client Secret.** Once generated, copy those credentials and keep them handy for use in the Airbyte UI later.

#### Step 5: Obtain your Endpoint and Identity URLs provided by Marketo

Follow the [Marketo documentation for obtaining your base URL](https://developers.marketo.com/rest-api/base-url/). Specifically, copy your **Endpoint** without "/rest" and keep them handy for use in the Airbyte UI.

We're almost there! Armed with your Endpoint & Identity URLs and your Client ID and Secret, head over to the Airbyte UI to setup Marketo as a source.

\*\*\*\*

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                    |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------|
| `0.1.4` | 2022-06-20 | [13930](https://github.com/airbytehq/airbyte/pull/13930) | Process failing creation of export jobs    |
| `0.1.3` | 2021-12-10 | [8429](https://github.com/airbytehq/airbyte/pull/8578)   | Updated titles and descriptions            |
| `0.1.2` | 2021-12-03 | [8483](https://github.com/airbytehq/airbyte/pull/8483)   | Improve field conversion to conform schema |
| `0.1.1` | 2021-11-29 | [0000](https://github.com/airbytehq/airbyte/pull/0000)   | Fix timestamp value format issue           |
| `0.1.0` | 2021-09-06 | [5863](https://github.com/airbytehq/airbyte/pull/5863)   | Release Marketo CDK Connector              |

