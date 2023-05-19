# Salesloft

This page contains the setup guide and reference information for the Salesloft Source connector.

## Prerequisites

- Salesloft Account
- Start date

<!-- env:oss -->
**For Airbyte Open Source:**

- Salesloft API Key (see [API Key Authentication](https://developers.salesloft.com/api.html#!/Topic/apikey))
<!-- /env:oss -->

## Setup guide

### Step 1: Set up Salesloft

Create a [Salesloft Account](https://salesloft.com).

<!-- env:oss -->
**Airbyte Open Source additional setup steps**

Log into [Salesloft](https://salesloft.com) and then generate an [API Key](https://developers.salesloft.com/api.html#!/Topic/apikey).
<!-- /env:oss -->

<!-- env:cloud -->
### Step 2: Set up the Salesloft connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Salesloft** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your Salesloft account` by selecting Oauth or API Key for Authentication.
5. Log in and Authorize to the Salesloft account.
6. Enter the **Start date** - The date from which you'd like to replicate data for streams.
7. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Authenticate with **API Key**.
<!-- /env:oss -->

## Supported sync modes

The Salesloft Source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

This connector outputs the following streams:

* [CadenceMemberships](https://developers.salesloft.com/api.html#!/Cadence_Memberships/get_v2_cadence_memberships_json)
* [Cadences](https://developers.salesloft.com/api.html#!/Cadences/get_v2_cadences_json)
* [People](https://developers.salesloft.com/api.html#!/People/get_v2_people_json)
* [Users](https://developers.salesloft.com/api.html#!/Users/get_v2_users_json)
* [Emails](https://developers.salesloft.com/api.html#!/Emails/get_v2_activities_emails_json)
* [Account Stages](https://developers.salesloft.com/api.html#!/Account_Stages/get_v2_account_stages_json)
* [Account Tiers](https://developers.salesloft.com/api.html#!/Account_Tiers/get_v2_account_tiers_json)
* [Accounts](https://developers.salesloft.com/api.html#!/Accounts/get_v2_accounts_json)
* [Actions](https://developers.salesloft.com/api.html#!/Actions/get_v2_actions_json)
* [Calls](https://developers.salesloft.com/api.html#!/Calls/get_v2_activities_calls_json)
* [Emails Templates](https://developers.salesloft.com/api.html#!/Email_Templates/get_v2_email_templates_json)
* [Emails Template Attachements](https://developers.salesloft.com/api.html#!/Email_Template_Attachments/get_v2_email_template_attachments_json)
* [Imports](https://developers.salesloft.com/api.html#!/Imports/get_v2_imports_json)
* [Notes](https://developers.salesloft.com/api.html#!/Notes/get_v2_notes_json)
* [Person Stages](https://developers.salesloft.com/api.html#!/Person_Stages/get_v2_person_stages_json)
* [Phone Number Assignments](https://developers.salesloft.com/api.html#!/Phone_Number_Assignments/get_v2_phone_number_assignments_json)
* [Steps](https://developers.salesloft.com/api.html#!/Steps/get_v2_steps_json)
* [Team Templates](https://developers.salesloft.com/api.html#!/Team_Templates/get_v2_team_templates_json)
* [Team Template Attachements](https://developers.salesloft.com/api.html#!/Team_Template_Attachments/get_v2_team_template_attachments_json)
* [CRM Activities](https://developers.salesloft.com/api.html#!/CRM_Activities/get_v2_crm_activities_json)
* [CRM Users](https://developers.salesloft.com/api.html#!/Crm_Users/get_v2_crm_users_json)
* [Groups](https://developers.salesloft.com/api.html#!/Groups/get_v2_groups_json)
* [Successes](https://developers.salesloft.com/api.html#!/Successes/get_v2_successes_json)

## Performance considerations

Salesloft has the [rate limits](hhttps://developers.salesloft.com/api.html#!/Topic/RateLimiting), but the Salesloft connector should not run into Salesloft API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                           |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------|
| 1.1.0   | 2023-05-17 | [26188](https://github.com/airbytehq/airbyte/pull/26188) | Added `latest_active_date` field to the `Cadences` stream schema. |
| 1.0.0   | 2023-03-08 | [23937](https://github.com/airbytehq/airbyte/pull/23937) | Certify to Beta                                                   |
| 0.1.6   | 2023-03-07 | [22893](https://github.com/airbytehq/airbyte/pull/22893) | Specified date formatting in specification                        |
| 0.1.5   | 2023-03-07 | [23828](https://github.com/airbytehq/airbyte/pull/23828) | Use `start_date` to filter data                                   |
| 0.1.4   | 2023-02-28 | [23564](https://github.com/airbytehq/airbyte/pull/23564) | Allow additional properties in spec and stream schemas            |
| 0.1.3   | 2022-03-28 | [11460](https://github.com/airbytehq/airbyte/pull/11460) | Added multiple new streams (Accounts, Actions, Calls, Notes ... ) |
| 0.1.3   | 2022-03-28 | [11460](https://github.com/airbytehq/airbyte/pull/11460) | Added multiple new streams (Accounts, Actions, Calls, Notes ... ) |
| 0.1.2   | 2022-03-17 | [11239](https://github.com/airbytehq/airbyte/pull/11239) | Added new Emails stream                                           |
| 0.1.1   | 2022-01-25 | [8617](https://github.com/airbytehq/airbyte/pull/8617)   | Update connector fields title/description                         |
| 0.1.0   | 2021-10-22 | [6962](https://github.com/airbytehq/airbyte/pull/6962)   | Salesloft Connector                                               |
