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

Note that there are no restrictions in naming the Vectara corpus and if a corpus with the specified name is not found, a new corpus with that name will be created. Also, if multiple corpora exists with the same name, an error will be returned as Airbyte will be unable to determine the preferred corpus.

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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                      |
|:--------| :--------- | :-------------------------------------------------------- | :----------------------------------------------------------- |
| 0.2.31 | 2024-11-25 | [48659](https://github.com/airbytehq/airbyte/pull/48659) | Update dependencies |
| 0.2.30 | 2024-11-04 | [48222](https://github.com/airbytehq/airbyte/pull/48222) | Update dependencies |
| 0.2.29 | 2024-10-29 | [47744](https://github.com/airbytehq/airbyte/pull/47744) | Update dependencies |
| 0.2.28 | 2024-10-23 | [47084](https://github.com/airbytehq/airbyte/pull/47084) | Update dependencies |
| 0.2.27 | 2024-10-12 | [46812](https://github.com/airbytehq/airbyte/pull/46812) | Update dependencies |
| 0.2.26 | 2024-10-05 | [46438](https://github.com/airbytehq/airbyte/pull/46438) | Update dependencies |
| 0.2.25 | 2024-09-28 | [46114](https://github.com/airbytehq/airbyte/pull/46114) | Update dependencies |
| 0.2.24 | 2024-09-21 | [45806](https://github.com/airbytehq/airbyte/pull/45806) | Update dependencies |
| 0.2.23 | 2024-09-14 | [45481](https://github.com/airbytehq/airbyte/pull/45481) | Update dependencies |
| 0.2.22 | 2024-09-07 | [45324](https://github.com/airbytehq/airbyte/pull/45324) | Update dependencies |
| 0.2.21 | 2024-08-31 | [45021](https://github.com/airbytehq/airbyte/pull/45021) | Update dependencies |
| 0.2.20 | 2024-08-24 | [44657](https://github.com/airbytehq/airbyte/pull/44657) | Update dependencies |
| 0.2.19 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.18 | 2024-08-17 | [44310](https://github.com/airbytehq/airbyte/pull/44310) | Update dependencies |
| 0.2.17 | 2024-08-12 | [43858](https://github.com/airbytehq/airbyte/pull/43858) | Update dependencies |
| 0.2.16 | 2024-08-10 | [43494](https://github.com/airbytehq/airbyte/pull/43494) | Update dependencies |
| 0.2.15 | 2024-08-03 | [43153](https://github.com/airbytehq/airbyte/pull/43153) | Update dependencies |
| 0.2.14 | 2024-07-27 | [42705](https://github.com/airbytehq/airbyte/pull/42705) | Update dependencies |
| 0.2.13 | 2024-07-20 | [42168](https://github.com/airbytehq/airbyte/pull/42168) | Update dependencies |
| 0.2.12 | 2024-07-13 | [41829](https://github.com/airbytehq/airbyte/pull/41829) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41362](https://github.com/airbytehq/airbyte/pull/41362) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41140](https://github.com/airbytehq/airbyte/pull/41140) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40953](https://github.com/airbytehq/airbyte/pull/40953) | Update dependencies |
| 0.2.8 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.2.7 | 2024-06-25 | [40321](https://github.com/airbytehq/airbyte/pull/40321) | Update dependencies |
| 0.2.6 | 2024-06-22 | [39973](https://github.com/airbytehq/airbyte/pull/39973) | Update dependencies |
| 0.2.5 | 2024-06-06 | [39193](https://github.com/airbytehq/airbyte/pull/39193) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-05-20 | [38432](https://github.com/airbytehq/airbyte/pull/38432) | [autopull] base image + poetry + up_to_date |
| 0.2.3   | 2024-03-22 | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Updated CDK & pytest version to fix security vulnerabilities |
| 0.2.2   | 2024-03-22 | [#36261](https://github.com/airbytehq/airbyte/pull/36261) | Move project to Poetry                                       |
| 0.2.1   | 2024-03-05 | [#35206](https://github.com/airbytehq/airbyte/pull/35206) | Fix: improved title parsing                                  |
| 0.2.0   | 2024-01-29 | [#34579](https://github.com/airbytehq/airbyte/pull/34579) | Add document title file configuration                        |
| 0.1.0   | 2023-11-10 | [#31958](https://github.com/airbytehq/airbyte/pull/31958) | 🎉 New Destination: Vectara (Vector Database)                |

</details>
