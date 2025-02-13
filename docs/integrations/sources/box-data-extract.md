# Box Data Extract
The Box Connector enables seamless data extraction from Box, allowing users to access file content from their Box cloud storage. This connector helps automate workflows by integrating Box files extracted data with other tools.

<HideInUI>

This page contains the setup guide and reference information for the [Box Data Extract](https://developer.box.com/) source connector.

</HideInUI>

## Prerequisites

You will need a [Box application](https://app.box.com/developers/console) configured to use Client Credential Grants (CCG)
Follow [this](https://developer.box.com/guides/authentication/client-credentials/) guide to complete authentication.

From your box app configuration take note of:
- `Client ID`: You Box App client ID. Find yours in the [Box App configurations](https://app.box.com/developers/console).
- `Client Secret`: You Box App client secret.

Decide on what account is going to login to Box:
- `Box Subject Type`: Represents the type of user to login as ("user" or "enterprise"). Enterprise will login with the application service account. User will login with the user if app can impersonate users.
- `Box Subject ID`: If subject type is "enterprise", use your enterprise ID If subject type is "user", use the user id to login as.

Choose the which Box folder conatins the files you want to process:
- `Folder ID`: Folder to retreive data from.
- `Recursive`: Read the folders recursively.

If you are using Box AI you'll need:
- `Ask AI Prompt`: If using the Ask AI, what prompt to send the AI about the document
- `Extract AI Prompt`: If using the Extract AI, what prompt to send the AI about the document

## Setup guide

## Set up Box Data Extract


### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Box Data Extract from the Source type dropdown.
4. Enter a name for the Box Data Extract connector.
5. Fill in the information:
    1. `Client ID`
    2. `Client Secret`
    3. `Box Subject Type`
    4. `Box Subject ID`
    5. `Folder ID`
    6. `Recursive`
6. Click **Setup source**



### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Box Data Extract from the Source type dropdown.
4. Enter a name for the Box Data Extract connector.
5. Fill in the information:
    1. `Client ID`
    2. `Client Secret`
    3. `Box Subject Type`
    4. `Box Subject ID`
    5. `Folder ID`
    6. `Recursive`
6. Click **Setup source**


## Supported sync modes

The Box Data Extract source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported Streams

- [File text extraction](https://developer.box.com/guides/representations/text/): Extract a text representation from your Box documents
- [AI Ask](https://developer.box.com/guides/box-ai/ai-tutorials/ask-questions/): Ask AI something about your Box documents
- [AI Extract](https://developer.box.com/guides/box-ai/ai-tutorials/extract-metadata/): Extract structured data from your Box documents


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.6 | 2025-02-13 | | Adding Box Extract AI stream |
| 0.1.5 | 2025-02-13 | | Adding Box Ask AI stream |
| 0.1.4 | 2025-02-12 | | Initial release by [@BoxDevRel](https://github.com/box-community/airbyte) |

</details>
