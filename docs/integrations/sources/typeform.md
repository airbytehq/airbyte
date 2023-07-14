# Typeform

This page guides you through the process of setting up the Typeform source connector.

## Prerequisites

* token - The Typeform API key token.
* start\_date - Date to start fetching Responses stream data from.
* form_ids (Optional) - List of Form Ids to sync. If not passed - sync all account`s forms.

## Setup guide

### Step 1: Set up Typeform

To get the API token for your application follow this [steps](https://developer.typeform.com/get-started/personal-access-token/)

* Log in to your account at Typeform.
* In the upper-right corner, in the drop-down menu next to your profile photo, click My Account.
* In the left menu, click Personal tokens.
* Click Generate a new token.
* In the Token name field, type a name for the token to help you identify it.
* Choose needed scopes \(API actions this token can perform - or permissions it has\). See here for more details on scopes.
* Click Generate token.

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Typeform** from the Source type dropdown and enter a name for this connector.
4. Fill-in 'API Token' and 'Start Date'
5. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the Set up the source page, enter the name for the connector and select **Tiktok Marketing** from the Source type dropdown.
4. Fill-in 'API Token' and 'Start Date'
5. click `Set up source`.
<!-- /env:oss -->

## Supported streams and sync modes

| Stream     | Key         | Incremental | API Link                                                                    |
|:-----------|-------------|:------------|-----------------------------------------------------------------------------|
| Forms      | id          | No          | https://developer.typeform.com/create/reference/retrieve-form/              |
| Responses  | response_id | Yes         | https://developer.typeform.com/responses/reference/retrieve-responses       |
| Webhooks   | id          | No          | https://developer.typeform.com/webhooks/reference/retrieve-webhooks/        |
| Workspaces | id          | No          | https://developer.typeform.com/create/reference/retrieve-workspaces/        |
| Images     | id          | No          | https://developer.typeform.com/create/reference/retrieve-images-collection/ |
| Themes     | id          | No          | https://developer.typeform.com/create/reference/retrieve-themes/            |

## Performance considerations

Typeform API page size limit per source:

* Forms - 200
* Responses - 1000

Connector performs additional API call to fetch all possible `form ids` on an account using [retrieve forms endpoint](https://developer.typeform.com/create/reference/retrieve-forms/)

API rate limits \(2 requests per second\): [https://developer.typeform.com/get-started/\#rate-limits](https://developer.typeform.com/get-started/#rate-limits)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.2.0  | 2023-06-17 | [27455](https://github.com/airbytehq/airbyte/pull/27455) | Add missing schema fields in `forms`, `themes`, `images`, `workspaces`, and `responses` streams                                                   |
| 0.1.12  | 2023-02-21 | [22824](https://github.com/airbytehq/airbyte/pull/22824) | Specified date formatting in specification                                                   |
| 0.1.11  | 2023-02-20 | [23248](https://github.com/airbytehq/airbyte/pull/23248) | Store cursor value as a string                                          |
| 0.1.10  | 2023-01-07 | [16125](https://github.com/airbytehq/airbyte/pull/16125) | Certification to Beta                                                   |
| 0.1.9   | 2022-08-30 | [16125](https://github.com/airbytehq/airbyte/pull/16125) | Improve `metadata.referer` url parsing                                  |
| 0.1.8   | 2022-08-09 | [15435](https://github.com/airbytehq/airbyte/pull/15435) | Update Forms   stream schema                                            |
| 0.1.7   | 2022-06-20 | [13935](https://github.com/airbytehq/airbyte/pull/13935) | Update Responses stream schema                                          |
| 0.1.6   | 2022-05-23 | [12280](https://github.com/airbytehq/airbyte/pull/12280) | Full Stream Coverage                                                    |
| 0.1.4   | 2021-12-08 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                |
| 0.1.3   | 2021-12-07 | [8466](https://github.com/airbytehq/airbyte/pull/8466)   | Change Check Connection Function Logic                                  |
| 0.1.2   | 2021-10-11 | [6571](https://github.com/airbytehq/airbyte/pull/6571)   | Support pulling data from a select set of forms                         |
| 0.1.1   | 2021-09-06 | [5799](https://github.com/airbytehq/airbyte/pull/5799)   | Add missed choices field to responses schema                            |
| 0.1.0   | 2021-07-10 | [4541](https://github.com/airbytehq/airbyte/pull/4541)   | Initial release for Typeform API supporting Forms and Responses streams |

