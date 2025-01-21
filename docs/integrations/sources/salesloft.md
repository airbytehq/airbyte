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

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following streams:

- [CadenceMemberships](https://developers.salesloft.com/api.html#!/Cadence_Memberships/get_v2_cadence_memberships_json)
- [Cadences](https://developers.salesloft.com/api.html#!/Cadences/get_v2_cadences_json)
- [People](https://developers.salesloft.com/api.html#!/People/get_v2_people_json)
- [Users](https://developers.salesloft.com/api.html#!/Users/get_v2_users_json)
- [Emails](https://developers.salesloft.com/api.html#!/Emails/get_v2_activities_emails_json)
- [Account Stages](https://developers.salesloft.com/api.html#!/Account_Stages/get_v2_account_stages_json)
- [Account Tiers](https://developers.salesloft.com/api.html#!/Account_Tiers/get_v2_account_tiers_json)
- [Accounts](https://developers.salesloft.com/api.html#!/Accounts/get_v2_accounts_json)
- [Actions](https://developers.salesloft.com/api.html#!/Actions/get_v2_actions_json)
- [Calls](https://developers.salesloft.com/api.html#!/Calls/get_v2_activities_calls_json)
- [Emails Templates](https://developers.salesloft.com/api.html#!/Email_Templates/get_v2_email_templates_json)
- [Emails Template Attachements](https://developers.salesloft.com/api.html#!/Email_Template_Attachments/get_v2_email_template_attachments_json)
- [Imports](https://developers.salesloft.com/api.html#!/Imports/get_v2_imports_json)
- [Notes](https://developers.salesloft.com/api.html#!/Notes/get_v2_notes_json)
- [Person Stages](https://developers.salesloft.com/api.html#!/Person_Stages/get_v2_person_stages_json)
- [Phone Number Assignments](https://developers.salesloft.com/api.html#!/Phone_Number_Assignments/get_v2_phone_number_assignments_json)
- [Steps](https://developers.salesloft.com/api.html#!/Steps/get_v2_steps_json)
- [Team Templates](https://developers.salesloft.com/api.html#!/Team_Templates/get_v2_team_templates_json)
- [Team Template Attachements](https://developers.salesloft.com/api.html#!/Team_Template_Attachments/get_v2_team_template_attachments_json)
- [CRM Activities](https://developers.salesloft.com/api.html#!/CRM_Activities/get_v2_crm_activities_json)
- [CRM Users](https://developers.salesloft.com/api.html#!/Crm_Users/get_v2_crm_users_json)
- [Groups](https://developers.salesloft.com/api.html#!/Groups/get_v2_groups_json)
- [Successes](https://developers.salesloft.com/api.html#!/Successes/get_v2_successes_json)
- [Call Data Records](https://developers.salesloft.com/api.html#!/Call_Data_Records/get_v2_call_data_records_json)
- [Call Dispositions](https://developers.salesloft.com/api.html#!/Call_Dispositions/get_v2_call_dispositions_json)
- [Call Sentiments](https://developers.salesloft.com/api.html#!/Call_Sentiments/get_v2_call_sentiments_json)
- [Custom Fields](https://developers.salesloft.com/api.html#!/Custom_Fields/get_v2_custom_fields_json)
- [Meetings](https://developers.salesloft.com/api.html#!/Meetings/get_v2_meetings_json)
- [Searches](https://developers.salesloft.com/api.html#!/Searches/post_v2_searches_json)

## Performance considerations

Salesloft has the [rate limits](hhttps://developers.salesloft.com/api.html#!/Topic/RateLimiting), but the Salesloft connector should not run into Salesloft API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                           |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------- |
| 1.2.23 | 2024-10-12 | [46833](https://github.com/airbytehq/airbyte/pull/46833) | Update dependencies |
| 1.2.22 | 2024-10-05 | [46491](https://github.com/airbytehq/airbyte/pull/46491) | Update dependencies |
| 1.2.21 | 2024-09-28 | [46186](https://github.com/airbytehq/airbyte/pull/46186) | Update dependencies |
| 1.2.20 | 2024-09-21 | [45726](https://github.com/airbytehq/airbyte/pull/45726) | Update dependencies |
| 1.2.19 | 2024-09-14 | [45500](https://github.com/airbytehq/airbyte/pull/45500) | Update dependencies |
| 1.2.18 | 2024-09-07 | [45238](https://github.com/airbytehq/airbyte/pull/45238) | Update dependencies |
| 1.2.17 | 2024-08-31 | [44967](https://github.com/airbytehq/airbyte/pull/44967) | Update dependencies |
| 1.2.16 | 2024-08-24 | [44642](https://github.com/airbytehq/airbyte/pull/44642) | Update dependencies |
| 1.2.15 | 2024-08-17 | [44301](https://github.com/airbytehq/airbyte/pull/44301) | Update dependencies |
| 1.2.14 | 2024-08-12 | [43910](https://github.com/airbytehq/airbyte/pull/43910) | Update dependencies |
| 1.2.13 | 2024-08-10 | [43524](https://github.com/airbytehq/airbyte/pull/43524) | Update dependencies |
| 1.2.12 | 2024-08-03 | [43051](https://github.com/airbytehq/airbyte/pull/43051) | Update dependencies |
| 1.2.11 | 2024-07-27 | [42800](https://github.com/airbytehq/airbyte/pull/42800) | Update dependencies |
| 1.2.10 | 2024-07-20 | [42258](https://github.com/airbytehq/airbyte/pull/42258) | Update dependencies |
| 1.2.9 | 2024-07-13 | [41699](https://github.com/airbytehq/airbyte/pull/41699) | Update dependencies |
| 1.2.8 | 2024-07-10 | [41532](https://github.com/airbytehq/airbyte/pull/41532) | Update dependencies |
| 1.2.7 | 2024-07-10 | [41327](https://github.com/airbytehq/airbyte/pull/41327) | Update dependencies |
| 1.2.6 | 2024-07-06 | [40896](https://github.com/airbytehq/airbyte/pull/40896) | Update dependencies |
| 1.2.5 | 2024-06-25 | [40437](https://github.com/airbytehq/airbyte/pull/40437) | Update dependencies |
| 1.2.4 | 2024-06-22 | [39974](https://github.com/airbytehq/airbyte/pull/39974) | Update dependencies |
| 1.2.3 | 2024-06-07 | [38362](https://github.com/airbytehq/airbyte/pull/38362) | Migrate to Low Code |
| 1.2.2 | 2024-06-04 | [39042](https://github.com/airbytehq/airbyte/pull/39042) | [autopull] Upgrade base image to v1.2.1 |
| 1.2.1 | 2024-05-20 | [38383](https://github.com/airbytehq/airbyte/pull/38383) | [autopull] base image + poetry + up_to_date |
| 1.2.0 | 2023-06-20 | [27505](https://github.com/airbytehq/airbyte/pull/27505) | Added new streams (Call Data Records, Call Dispositions, ... ) |
| 1.1.1 | 2023-06-17 | [27484](https://github.com/airbytehq/airbyte/pull/27484) | Bump version on py files updates |
| 1.1.0 | 2023-05-17 | [26188](https://github.com/airbytehq/airbyte/pull/26188) | Added `latest_active_date` field to the `Cadences` stream schema. |
| 1.0.0 | 2023-03-08 | [23937](https://github.com/airbytehq/airbyte/pull/23937) | Certify to Beta |
| 0.1.6 | 2023-03-07 | [22893](https://github.com/airbytehq/airbyte/pull/22893) | Specified date formatting in specification |
| 0.1.5 | 2023-03-07 | [23828](https://github.com/airbytehq/airbyte/pull/23828) | Use `start_date` to filter data |
| 0.1.4 | 2023-02-28 | [23564](https://github.com/airbytehq/airbyte/pull/23564) | Allow additional properties in spec and stream schemas |
| 0.1.3 | 2022-03-28 | [11460](https://github.com/airbytehq/airbyte/pull/11460) | Added multiple new streams (Accounts, Actions, Calls, Notes ... ) |
| 0.1.2 | 2022-03-17 | [11239](https://github.com/airbytehq/airbyte/pull/11239) | Added new Emails stream |
| 0.1.1 | 2022-01-25 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description |
| 0.1.0 | 2021-10-22 | [6962](https://github.com/airbytehq/airbyte/pull/6962) | Salesloft Connector | |

</details>
