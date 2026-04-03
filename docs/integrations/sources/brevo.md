# Brevo

<HideInUI>

This page contains the setup guide and reference information for the [Brevo](https://www.brevo.com/) source connector.

</HideInUI>

[Brevo](https://www.brevo.com/) (formerly Sendinblue) is a marketing and CRM platform that provides email campaigns, SMS campaigns, contact management, and sales CRM tools. This connector reads data from the [Brevo API v3](https://developers.brevo.com/reference).

## Prerequisites

- A Brevo account
- A Brevo API key. Generate one from your [SMTP & API settings](https://app.brevo.com/settings/keys/api) page.

## Setup guide

### Step 1: Generate a Brevo API key

1. Log in to your [Brevo account](https://app.brevo.com/).
2. Navigate to your profile icon, then select **SMTP & API**.
3. Under the **API Keys** tab, click **Generate a new API key**.
4. Name your key and click **Generate**.
5. Copy the API key immediately. You cannot view it again after closing the dialog.

### Step 2: Set up the Brevo connector in Airbyte

1. In the Airbyte UI, click **Sources**, then click **+ New source**.
2. Select **Brevo** from the source type dropdown.
3. Enter a **Name** for the connector.
4. Enter the **API Key** you generated in Step 1.
5. Enter a **Start date** in the format `YYYY-MM-DDTHH:MM:SSZ` (for example, `2024-01-01T00:00:00Z`). Only data created or modified on or after this date is synced for incremental streams.
6. Click **Set up source**.

<HideInUI>

## Supported sync modes

The Brevo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

The Brevo source connector supports the following streams:

| Stream | API endpoint | Sync mode | Primary key | Notes |
| --- | --- | --- | --- | --- |
| [contacts](https://developers.brevo.com/reference/get-contacts) | `/contacts` | Full Refresh, Incremental | `id` | Incremental cursor: `modifiedAt` |
| [contacts_attributes](https://developers.brevo.com/reference/get_contacts-attributes) | `/contacts/attributes` | Full Refresh | | Lists contact attribute definitions |
| [contacts_folders](https://developers.brevo.com/reference/get_contacts-folders) | `/contacts/folders` | Full Refresh | `id` | |
| [contacts_folders_lists](https://developers.brevo.com/reference/get_contacts-folders-folderid-lists) | `/contacts/folders/{folderId}/lists` | Full Refresh | `id` | Substream of `contacts_folders` |
| [contacts_segments](https://developers.brevo.com/reference/get_contacts-segments) | `/contacts/segments` | Full Refresh | `id` | |
| [contacts_lists](https://developers.brevo.com/reference/get_contacts-lists) | `/contacts/lists` | Full Refresh | `id` | |
| [contacts_lists_contacts](https://developers.brevo.com/reference/get_contacts-lists-listid-contacts) | `/contacts/lists/{listId}/contacts` | Full Refresh, Incremental | | Substream of `contacts_lists`. Incremental cursor: `modifiedAt` |
| [senders](https://developers.brevo.com/reference/get_senders) | `/senders` | Full Refresh | `id` | |
| [companies](https://developers.brevo.com/reference/get_companies) | `/companies` | Full Refresh, Incremental | `id` | Incremental cursor: `last_updated_at` |
| [companies_attributes](https://developers.brevo.com/reference/get_companies-attributes) | `/companies/attributes` | Full Refresh | | Lists company attribute definitions |
| [crm_pipeline_stages](https://developers.brevo.com/reference/get_crm-pipeline-details) | `/crm/pipeline/details` | Full Refresh | `id` | Returns pipeline stage definitions |
| [crm_pipeline_details_all](https://developers.brevo.com/reference/get_crm-pipeline-details-all) | `/crm/pipeline/details/all` | Full Refresh | `pipeline` | Returns all pipeline details |
| [crm_attributes_deals](https://developers.brevo.com/reference/get_crm-attributes-deals) | `/crm/attributes/deals` | Full Refresh | | Lists deal attribute definitions |
| [crm_deals](https://developers.brevo.com/reference/get_crm-deals) | `/crm/deals` | Full Refresh, Incremental | `id` | Incremental cursor: `last_updated_at` |
| [crm_tasktypes](https://developers.brevo.com/reference/get_crm-tasktypes) | `/crm/tasktypes` | Full Refresh | `id` | |
| [crm_tasks](https://developers.brevo.com/reference/get_crm-tasks) | `/crm/tasks` | Full Refresh, Incremental | `id` | Incremental cursor: `updatedAt` |
| [crm_notes](https://developers.brevo.com/reference/get_crm-notes) | `/crm/notes` | Full Refresh, Incremental | `id` | Incremental cursor: `updatedAt` |
| [domains](https://developers.brevo.com/reference/get_senders-domains) | `/senders/domains` | Full Refresh | `id` | |
| [webhooks](https://developers.brevo.com/reference/get_webhooks) | `/webhooks` | Full Refresh | `id` | No pagination |
| [account](https://developers.brevo.com/reference/get_account) | `/account` | Full Refresh | `organization_id` | |
| [organization_invited_users](https://developers.brevo.com/reference/get_organization-invited-users) | `/organization/invited/users` | Full Refresh | `email` | |
| [emailCampaigns](https://developers.brevo.com/reference/get-email-campaigns) | `/emailCampaigns` | Full Refresh, Incremental | `id` | Incremental cursor: `modifiedAt` |
| [smsCampaigns](https://developers.brevo.com/reference/get-sms-campaigns) | `/smsCampaigns` | Full Refresh, Incremental | `id` | Incremental cursor: `modifiedAt` |

## Limitations and troubleshooting

### Rate limits

The Brevo API enforces [rate limits](https://developers.brevo.com/docs/api-limits) that vary by account plan and endpoint. Most endpoints relevant to this connector fall under the general limit of 100 requests per hour on Free plans and higher limits on paid plans. Contacts endpoints have a limit of 36,000 requests per hour (10 requests per second).

The connector handles `429 Too Many Requests` responses with exponential backoff retries. If you experience frequent rate limiting, consider reducing sync frequency or upgrading your Brevo plan.

</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.2.30 | 2026-04-01 | [75946](https://github.com/airbytehq/airbyte/pull/75946) | Bump SDM base image for memory monitor (CDK PR #962) |
| 0.2.29 | 2026-03-31 | [75672](https://github.com/airbytehq/airbyte/pull/75672) | Update dependencies |
| 0.2.28 | 2026-03-24 | [75312](https://github.com/airbytehq/airbyte/pull/75312) | Update dependencies |
| 0.2.27 | 2026-02-17 | [73432](https://github.com/airbytehq/airbyte/pull/73432) | Update dependencies |
| 0.2.26 | 2026-02-03 | [72612](https://github.com/airbytehq/airbyte/pull/72612) | Update dependencies |
| 0.2.25 | 2026-01-20 | [72057](https://github.com/airbytehq/airbyte/pull/72057) | Update dependencies |
| 0.2.24 | 2026-01-14 | [71464](https://github.com/airbytehq/airbyte/pull/71464) | Update dependencies |
| 0.2.23 | 2025-12-18 | [70627](https://github.com/airbytehq/airbyte/pull/70627) | Update dependencies |
| 0.2.22 | 2025-11-25 | [69949](https://github.com/airbytehq/airbyte/pull/69949) | Update dependencies |
| 0.2.21 | 2025-11-18 | [69462](https://github.com/airbytehq/airbyte/pull/69462) | Update dependencies |
| 0.2.20 | 2025-10-29 | [68749](https://github.com/airbytehq/airbyte/pull/68749) | Update dependencies |
| 0.2.19 | 2025-10-21 | [68272](https://github.com/airbytehq/airbyte/pull/68272) | Update dependencies |
| 0.2.18 | 2025-10-14 | [67845](https://github.com/airbytehq/airbyte/pull/67845) | Update dependencies |
| 0.2.17 | 2025-10-07 | [67207](https://github.com/airbytehq/airbyte/pull/67207) | Update dependencies |
| 0.2.16 | 2025-09-30 | [65648](https://github.com/airbytehq/airbyte/pull/65648) | Update dependencies |
| 0.2.15 | 2025-08-09 | [64647](https://github.com/airbytehq/airbyte/pull/64647) | Update dependencies |
| 0.2.14 | 2025-07-12 | [63047](https://github.com/airbytehq/airbyte/pull/63047) | Update dependencies |
| 0.2.13 | 2025-07-05 | [62527](https://github.com/airbytehq/airbyte/pull/62527) | Update dependencies |
| 0.2.12 | 2025-06-28 | [62149](https://github.com/airbytehq/airbyte/pull/62149) | Update dependencies |
| 0.2.11 | 2025-06-21 | [61898](https://github.com/airbytehq/airbyte/pull/61898) | Update dependencies |
| 0.2.10 | 2025-06-15 | [61447](https://github.com/airbytehq/airbyte/pull/61447) | Update dependencies |
| 0.2.9 | 2025-05-24 | [60610](https://github.com/airbytehq/airbyte/pull/60610) | Update dependencies |
| 0.2.8 | 2025-05-10 | [59885](https://github.com/airbytehq/airbyte/pull/59885) | Update dependencies |
| 0.2.7 | 2025-05-05 | [59652](https://github.com/airbytehq/airbyte/pull/59652) | Fix contact pagination |
| 0.2.6 | 2025-05-03 | [58704](https://github.com/airbytehq/airbyte/pull/58704) | Update dependencies |
| 0.2.5 | 2025-04-24 | [57576](https://github.com/airbytehq/airbyte/pull/57576) | Set ordering in ascending on incremental streams |
| 0.2.4 | 2025-04-19 | [57595](https://github.com/airbytehq/airbyte/pull/57595) | Update dependencies |
| 0.2.3 | 2025-04-05 | [57126](https://github.com/airbytehq/airbyte/pull/57126) | Update dependencies |
| 0.2.2 | 2025-03-29 | [56622](https://github.com/airbytehq/airbyte/pull/56622) | Update dependencies |
| 0.2.1 | 2025-03-27 | [56437](https://github.com/airbytehq/airbyte/pull/56437) | Update contacts pagination page size to 1000 |
| 0.2.0 | 2025-03-24 | [56369](https://github.com/airbytehq/airbyte/pull/56369) | Fix/Add incremental on Contacts/Crm deals |
| 0.1.8 | 2025-03-22 | [55367](https://github.com/airbytehq/airbyte/pull/55367) | Update dependencies |
| 0.1.7 | 2025-03-01 | [54874](https://github.com/airbytehq/airbyte/pull/54874) | Update dependencies |
| 0.1.6 | 2025-02-25 | [54674](https://github.com/airbytehq/airbyte/pull/54674) | Fix bug authenticator |
| 0.1.5 | 2025-02-22 | [54223](https://github.com/airbytehq/airbyte/pull/54223) | Update dependencies |
| 0.1.4 | 2025-02-15 | [48282](https://github.com/airbytehq/airbyte/pull/48282) | Update dependencies |
| 0.1.3 | 2024-11-28 | [48737](https://github.com/airbytehq/airbyte/pull/48737) | Update pagination |
| 0.1.2 | 2024-10-29 | [47922](https://github.com/airbytehq/airbyte/pull/47922) | Update dependencies |
| 0.1.1 | 2024-10-28 | [47622](https://github.com/airbytehq/airbyte/pull/47622) | Update dependencies |
| 0.1.0 | 2024-10-08 | [46587](https://github.com/airbytehq/airbyte/pull/46587) | Fix Companies stream paginator+ remove incremental |
| 0.0.1 | 2024-09-11 | [45382](https://github.com/airbytehq/airbyte/pull/45382) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
