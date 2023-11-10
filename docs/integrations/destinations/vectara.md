# Vectara

This page contains the setup guide and reference information for the Vectara destination connector.

Get started with Vectara at the [Vectara website](https://vectara.com/). For more details about how Vectara works, see the [Vectara documentation](https://docs.vectara.com/)

## Overview

The Vectara destination connector supports Full Refresh Overwrite, Full Refresh Append, and Incremental Append.

### Output schema

All streams will be output into a corpus in Vectara whose name must be specified in the config. 

Note that there are no restrictions in naming the Vectara corpus and if a corpus with the specified name is not found, a new corpus with that name will be created. Also, if multiple corpora exists with the same name, an error will be returned as Airbyte will be unable to determine the prefered corpus.


### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | Yes        |
| Incremental - Dedupe Sync     | No         |


## Getting started

### Requirements

- [Vectara Account](https://console.vectara.com/signup)
- [Vectara Corpus](https://docs.vectara.com/docs/console-ui/creating-a-corpus)
- [OAuth2.0 Credentials](https://docs.vectara.com/docs/learn/authentication/oauth-2)

### Setup the Chroma Destination in Airbyte

You should now have all the requirements needed to configure Chroma as a destination in the UI. You'll need the following information to configure the Chroma destination:

- (Required) OAuth2.0 Credentials
  - (Required) **Client ID**
  - (Required) **Client Secret**
- (Required) **Customer ID**
- (Required) **Corpus Name**

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                           |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------- |
| 0.1.0   | 2023-11-10 | [31958](https://github.com/airbytehq/airbyte/pull/31958) | 🎉 New Destination: Vectara (Vector Database)                     |
