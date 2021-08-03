# Google Search Console

## Overview

The Google Search Console source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source wraps the [Singer Google Search Console Tap](https://github.com/singer-io/tap-google-search-console).

### Output schema

This Source is capable of syncing the following Streams:

* [Sites](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites/get)
* [Sitemaps](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps/list)
* [Performance report country](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report custom](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report date](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report device](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report page](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Performance report query \(keyword\)](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes | except Sites and Sitemaps |
| SSL connection | Yes |  |
| Namespaces | No |  |

### Performance considerations

This connector attempts to back off gracefully when it hits Reports API's rate limits. To find more information about limits, see [Usage Limits](https://developers.google.com/webmaster-tools/search-console-api-original/v3/limits) documentation.

## Getting started

### Requirements

* Credentials to a Google Service Account (or Google Service Account with delegated Domain Wide Authority)
* Email address of the workspace admin who created the Service Account

## How to create the client credentials for Google Search Console, to use with Airbyte?

You can either:
* Use the existing `Service Account` for your Google Project with granted Admin Permissions
* Create the new `Service Account` credentials for your Google Project, and grant Admin Permissions to it
* Follow the `Delegating domain-wide authority` process to obtain the necessary permissions to your google account from the administrator of Workspace

### Creating a Google service account
A service account's credentials include a generated email address that is unique and at least one public/private key pair. If domain-wide delegation is enabled, then a client ID is also part of the service account's credentials.

1. Open the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts)
2. If prompted, select an existing project, or create a new project.
3. Click `+ Create service account`.
4. Under Service account details, type a `name`, `ID`, and `description` for the service account, then click `Create`.
  * Optional: Under `Service account permissions`, select the `IAM roles` to grant to the service account, then click `Continue`.
  * Optional: Under `Grant users access to this service account`, add the `users` or `groups` that are allowed to use and manage the service account.
5. Go to [API Console/Credentials](https://console.cloud.google.com/apis/credentials), check the `Service Accounts` section, click on the Email address of service account you just created. 
6. Open `Details` tab and find `Show domain-wide delegation`, checkmark the `Enable Google Workspace Domain-wide Delegation`.
7. On `Keys` tab click `+ Add key`, then click `Create new key`.

Your new public/private key pair should be now generated and downloaded to your machine as `<project_id>.json` you can find it in the `Downloads` folder or somewhere else if you use another default destination for downloaded files. This file serves as the only copy of the private key. You are responsible for storing it securely.
If you lose this key pair, you will need to generate a new one!

### Using the existing Service Account 
1. Go to [API Console/Credentials](https://console.cloud.google.com/apis/credentials), check the `Service Accounts` section, click on the Email address of service account you just created.
2. Click on `Details` tab and find `Show domain-wide delegation`, checkmark the `Enable Google Workspace Domain-wide Delegation`.
2. On `Keys` tab click `+ Add key`, then click `Create new key`.

Your new public/private key pair should be now generated and downloaded to your machine as `<project_id>.json` you can find it in the `Downloads` folder or somewhere else if you use another default destination for downloaded files. This file serves as the only copy of the private key. You are responsible for storing it securely.
If you lose this key pair, you will need to generate a new one!

### Note
You can return to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) at any time to view the email address, public key fingerprints, and other information, or to generate additional public/private key pairs. For more details about service account credentials in the API Console, see [Service accounts](https://cloud.google.com/iam/docs/understanding-service-accounts) in the API Console help file.

### Create a Service Account with delegated domain-wide authority

Follow the Google Documentation for performing [Delegating domain-wide authority](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority) to create a Service account with delegated domain-wide authority. This account must be created by an administrator of your Google Workspace. Please make sure to grant the following `OAuth scopes` to the service user:

* `https://www.googleapis.com/auth/webmasters.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account.

You should now be ready to use the Google Workspace Admin Reports API connector in Airbyte.

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.3` | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
