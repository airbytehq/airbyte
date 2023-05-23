# The Guardian API Source Connector

## Overview

The Guardian API source connector syncs data from [The Guardian Open Platform](https://open-platform.theguardian.com/), which allows access to The Guardian's online content, including articles and tags.

## Requirements

To use the Guardian API source connector, you will need an API key. To get one, follow these steps:

1. Visit [The Guardian Open Platform Access page](https://open-platform.theguardian.com/access).
2. Click "Register Now" to create an account or sign in with your existing Guardian account.
3. Fill out the required fields and select "API" as your preferred access method.
4. Accept the terms and conditions, then click on "Register."
5. You should now have access to your API key.

Save your API key, as it will be needed later when setting up the connector in Airbyte.

## Optional Parameters

You can customize the data you sync from The Guardian API using the following optional parameters:

- `query` (q): Filters the results to only those that include the search term. The query parameter supports `AND`, `OR`, and `NOT` operators.
- `tag`: Filters the results to show only the ones matching the entered tag.
- `section`: Filters the results by a particular section.
- `order-by`: Sorts the results by `newest`, `oldest`, or `relevance`.
- `start_date` (YYYY-MM-DD): Specifies the minimum date of the results. Articles older than the given start date will not be synced.
- `end_date` (YYYY-MM-DD): Specifies the maximum date of the results. Articles newer than the given end date will not be synced.

For more information on the optional parameters and their use, please refer to the original documentation above.

## Setup Guide

To set up the Guardian API source connector in Airbyte, follow these steps:

1. Access the source connector configuration form in the Airbyte UI.
2. Enter your `api_key` (mandatory) obtained earlier into the "API Key" field.
3. (Optional) Customize your sync by entering values for the optional parameters (`query`, `tag`, `section`, `order-by`, `start_date`, and `end_date`) as per your requirements.
4. Click **Save & Continue** to set up the source.

## Supported Sync Modes

The Guardian API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Performance Considerations

The Guardian API key is rate-limited, which means that applications making a large number of requests on a polling basis may exceed their daily quota and be prevented from making further requests until the next period begins. Make sure to plan your requests accordingly.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                        |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18654](https://github.com/airbytehq/airbyte/pull/18654) | 🎉 New Source: The Guardian API [low-code CDK] |

