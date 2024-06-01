# Vectara

This page contains the setup guide and reference information for the Vectara destination connector.

[Vectara](https://vectara.com/) is the trusted GenAI platform that provides Retrieval Augmented Generation or [RAG](https://vectara.com/grounded-generation/) as a service.

The Vectara destination connector allows you to connect any Airbyte source to Vectara and ingest data into Vectara for your RAG pipeline.

:::info
In case of issues, the following public channels are available for support:

- For Airbyte related issues such as data source or processing: [Open a Github issue](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug%2Carea%2Fconnectors%2Cneeds-triage&projects=&template=1-issue-connector.yaml)
- For Vectara related issues such as data indexing or RAG: Create a post in the [Vectara forum](https://discuss.vectara.com/) or reach out on [Vectara's Discord server](https://discord.gg/GFb8gMz6UH)

:::

## Overview

The Vectara destination connector supports Full Refresh Overwrite, Full Refresh Append, and Incremental Append.

### Output schema

All streams will be output into a corpus in Vectara whose name must be specified in the config.

Note that there are no restrictions in naming the Vectara corpus and if a corpus with the specified name is not found, a new corpus with that name will be created. Also, if multiple corpora exists with the same name, an error will be returned as Airbyte will be unable to determine the prefered corpus.

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |

## Getting started

You will need a Vectara account to use Vectara with Airbyte. To get started, use the following steps:

1. [Sign up](https://vectara.com/integrations/airbyte) for a Vectara account if you don't already have one. Once you have completed your sign up you will have a Vectara customer ID. You can find your customer ID by clicking on your name, on the top-right of the Vectara console window.
2. Within your account you can create your corpus, which represents an area that stores text data you want to ingest into Vectara.
   - To create a corpus, use the **"Create Corpus"** button in the console. You then provide a name to your corpus as well as a description. If you click on your created corpus, you can see its name and corpus ID right on the top. You can see more details in this [guide](https://docs.vectara.com/docs/console-ui/creating-a-corpus).
   - Optionally you can define filtering attributes and apply some advanced options.
   - For the Vectara connector to work properly you **must** define a special meta-data field called `_ab_stream` (string typed) which the connector uses to identify source streams.
3. The Vectara destination connector uses [OAuth2.0 Credentials](https://docs.vectara.com/docs/learn/authentication/oauth-2). You will need your `Client ID` and `Client Secret` handy for your connector setup.

### Setup the Vectara Destination in Airbyte

You should now have all the requirements needed to configure Vectara as a destination in the UI.

You'll need the following information to configure the Vectara destination:

- (Required) OAuth2.0 Credentials
  - (Required) **Client ID**
  - (Required) **Client Secret**
- (Required) **Customer ID**
- (Required) **Corpus Name**. You can specify a corpus name you've setup manually given the instructions above, or if you specify a corpus name that does not exist, the connector will generate a new corpus in this name and setup the required meta-data filtering fields within that corpus.

In addition, in the connector UI you define two set of fields for this connector:

- `text_fields` define the source fields which are turned into text in the Vectara side and are used for query or summarization.
- `title_field` define the source field which will be used as a title of the document on the Vectara side
- `metadata_fields` define the source fields which will be added to each document as meta-data.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                      |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------------------------- |
| 0.2.4 | 2024-05-20 | [38432](https://github.com/airbytehq/airbyte/pull/38432) | [autopull] base image + poetry + up_to_date |
| 0.2.3   | 2024-03-22 | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Updated CDK & pytest version to fix security vulnerabilities |
| 0.2.2   | 2024-03-22 | [#36261](https://github.com/airbytehq/airbyte/pull/36261) | Move project to Poetry                                       |
| 0.2.1   | 2024-03-05 | [#35206](https://github.com/airbytehq/airbyte/pull/35206) | Fix: improved title parsing                                  |
| 0.2.0   | 2024-01-29 | [#34579](https://github.com/airbytehq/airbyte/pull/34579) | Add document title file configuration                        |
| 0.1.0   | 2023-11-10 | [#31958](https://github.com/airbytehq/airbyte/pull/31958) | 🎉 New Destination: Vectara (Vector Database)                |
