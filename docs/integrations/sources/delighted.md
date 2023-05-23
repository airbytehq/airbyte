# Delighted Source Connector

This page contains the setup guide and reference information for the Delighted source connector in Airbyte.

## Prerequisites

Before setting up the Delighted source connector, you'll need the following:

1. A Delighted account with the necessary permissions to access the API.
2. Delighted API key.

To obtain the API key from your Delighted account, follow these steps:

1. Log into your Delighted account.
2. Click on the **Settings** icon in the top right corner and select **API** from the menu.
3. On the API settings page, you will find your API key. Copy this key as it will be required for configuring the Delighted source connector in Airbyte.

Refer to the [Delighted API documentation](https://api.delighted.com/docs/) for more information.

## Set up the Delighted Connector in Airbyte

1. Begin by providing a **name** for your Delighted connector. This can be any name that you find descriptive.
2. For **API Key**, enter the Delighted API key you obtained in the Prerequisites section.
3. For **Since**, enter the starting date from which you'd like to replicate the data in either an `RFC3339` format like `2022-05-30T04:50:23Z` or a `datetime string` format like `2022-05-30 04:50:23`. Any data added on and after this date will be replicated.
4. After filling in the required fields, click **Set up source**.

Now, the Delighted source connector is set up and ready to use in Airbyte.

Please note that the content above provides only the updated setup section for the Delighted source connector in Airbyte. The rest of the documentation remains unchanged, including the Changelog and any tables in the original document. No images have been assumed or included in this response.