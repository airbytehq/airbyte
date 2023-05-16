# Aha API

API Documentation link [here](https://www.aha.io/api)

## Overview

The Aha API source in Airbyte supports full refresh syncs for the following output streams:

- [features](https://www.aha.io/api/resources/features/list_features)
- [products](https://www.aha.io/api/resources/products/list_products_in_the_account)

## Getting started

### Requirements

Before you begin:

- You need an Aha API Key.
- You need to have an Aha account.

### Creating an Aha API Key

To obtain an API key:

1. Log in to your Aha account.
2. Click on your name in the top menu and select Settings.
3. On the left side of the Settings page, choose API Keys.
4. Click on the Create API Key button.

![create-api-key](https://dl.airtable.com/.attachmentThumbnails/99e34d05f1c2cae09390fd94b05d3d6b/5bf16a5c)

5. Provide a name for your API key and choose its expiration date.
6. Click on the Create API Key button.

![create-api-key-form](https://dl.airtable.com/.attachmentThumbnails/e57bb5d38f01a3b0c7b557a2d4c40176/e4e438ba)

7. Copy the generated API key as it will only be shown once.
8. Keep your API key safe as anyone can read, edit and delete with this key.

### Configuring the Aha API source connector

To configure the Aha API source connector:

1. Fill in the form fields as follows:

- `API Bearer Token`: Paste the Aha API Key you created earlier.
- `Aha Url Instance`: Enter your Aha instance URL without the `https://` and the trailing slash.

![configure-aha-form](https://dl.airtable.com/.attachmentThumbnails/b653159caf0f6a5f542ded653fc87653/93381e21)

2. Click on the Test button to verify that the connection is working.

![test-connection-button](https://dl.airtable.com/.attachmentThumbnails/0ca082166c1cdd0fd933b63fe21ca6b2/a8a4dcab)

3. Save the configuration by clicking on the Save button.

Congratulations! You have completed the configuration of the Aha API source connector and you are ready to replicate your data.