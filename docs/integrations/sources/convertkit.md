# ConvertKit

This page guides you through setting up the ConvertKit source connector, which syncs data from [Kit](https://kit.com/) (formerly ConvertKit) using the [Kit API v4](https://developers.kit.com/api-reference/overview).

## Prerequisites

- A Kit account on a plan that's [eligible for API access](https://kit.com/pricing).
- One of the following sets of credentials:
  - A Kit **V4 API key**. API keys only access your own Kit account and have a lower rate limit than OAuth.
  - OAuth 2.0 credentials from a Kit app: a **Client ID**, **Client Secret**, and **Refresh Token**. OAuth is required to sync the `purchases` stream.

Kit V3 API keys and API secrets don't work with the V4 API. If you only have V3 credentials, create a V4 API key.

## Setup guide

### Step 1: Get your Kit credentials

#### Option A: API key

1. In Kit, go to **Settings** > [**Developer**](https://app.kit.com/account_settings/developer_settings).
2. Create a new V4 API key.
3. Copy the API key and store it somewhere safe. Kit only shows the key once. If you lose it, you must reset the key.

For more details, see [Creating V4 API keys](https://developers.kit.com/api-reference/authentication#creating-v4-api-keys).

#### Option B: OAuth 2.0

1. [Create a Kit app](https://developers.kit.com/kit-app-store/building-apps#creating-your-app) and turn on API access for it.
2. Configure the app's redirect URI, then copy the app's **Client ID** and **Client Secret**.
3. Complete Kit's [OAuth authorization code flow](https://developers.kit.com/api-reference/oauth-refresh-token-flow) for the Kit account you want to sync, and save the **Refresh Token** that Kit returns.

The connector uses the refresh token to request access tokens from `https://api.kit.com/oauth/token` and stores the rotated refresh token in your connection configuration.

### Step 2: Set up the ConvertKit connector in Airbyte

1. In Airbyte, go to **Sources** and select **ConvertKit**.
2. Enter a name for the source.
3. For **Start date**, enter the UTC date and time from which to sync subscriber records, in the format `YYYY-MM-DDTHH:mm:ssZ`. The default is `2013-01-01T00:00:00Z`. The start date only applies to the `subscribers`, `form_subscribers`, `sequence_subscribers`, and `tag_subscribers` streams.
4. For **Authentication Type**, choose one of the following:
   - **API Key**: Enter your V4 API key.
   - **OAuth 2.0**: Enter your **Client ID**, **Client Secret**, and **Refresh Token**. You can leave **Access Token** and **Access Token Expires At** empty. The connector fills them in when it refreshes the token.
5. Click **Set up source**.

## Supported sync modes

| Feature           | Supported? | Notes                                                                                 |
| :---------------- | :--------- | :------------------------------------------------------------------------------------ |
| Full Refresh Sync | Yes        |                                                                                       |
| Incremental Sync  | Yes        | `subscribers`, `form_subscribers`, `sequence_subscribers`, and `tag_subscribers` only |

## Supported streams

| Stream                 | Kit API endpoint                                                                                                      | Primary key         | Incremental |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------------- | :------------------ | :---------- |
| `broadcasts`           | [List broadcasts](https://developers.kit.com/api-reference/broadcasts/list-broadcasts)                                | `id`                | No          |
| `current_account`      | [Get current account](https://developers.kit.com/api-reference/accounts/get-current-account)                          | None                | No          |
| `custom_fields`        | [List custom fields](https://developers.kit.com/api-reference/custom-fields/list-custom-fields)                       | `id`                | No          |
| `email_templates`      | [List email templates](https://developers.kit.com/api-reference/email-templates/list-email-templates)                 | `id`                | No          |
| `forms`                | [List forms](https://developers.kit.com/api-reference/forms/list-forms)                                               | `id`                | No          |
| `form_subscribers`     | [List subscribers for a form](https://developers.kit.com/api-reference/forms/list-subscribers-for-a-form)             | `id`, `form_id`     | Yes         |
| `purchases`            | [List purchases](https://developers.kit.com/api-reference/purchases/list-purchases)                                   | `id`                | No          |
| `segments`             | [List segments](https://developers.kit.com/api-reference/segments/list-segments)                                      | `id`                | No          |
| `sequences`            | [List sequences](https://developers.kit.com/api-reference/sequences/list-sequences)                                   | `id`                | No          |
| `sequence_subscribers` | [List subscribers for a sequence](https://developers.kit.com/api-reference/sequences/list-subscribers-for-a-sequence) | `id`, `sequence_id` | Yes         |
| `subscribers`          | [List subscribers](https://developers.kit.com/api-reference/subscribers/list-subscribers)                             | `id`                | Yes         |
| `tags`                 | [List tags](https://developers.kit.com/api-reference/tags/list-tags)                                                  | `id`                | No          |
| `tag_subscribers`      | [List subscribers for a tag](https://developers.kit.com/api-reference/tags/list-subscribers-for-a-tag)                | `id`, `tag_id`      | Yes         |

The `form_subscribers`, `sequence_subscribers`, and `tag_subscribers` streams read every form, sequence, or tag first, then request the subscribers for each one. The connector adds `form_id`, `sequence_id`, or `tag_id` to each record.

The subscriber streams request subscribers in all states, including inactive, bounced, complained, and cancelled subscribers, not only active ones.

### Incremental sync behavior

- `subscribers`: Filters on the subscriber's last update time (`updated_after`). The cursor field, `date_last_loaded`, is added by the connector and records when the sync read the record.
- `tag_subscribers`: Filters on when the subscriber was tagged (`tagged_after`). The cursor field, `date_loaded`, is added by the connector and records when the sync read the record.
- `form_subscribers` and `sequence_subscribers`: Filter on when the subscriber was added (`added_after`), using the `added_at` field as the cursor.

Each incremental sync re-reads the last hour before the saved cursor, so expect some duplicate records unless you use a deduplicating sync mode.

## Limitations and troubleshooting

### Rate limits

Kit limits API keys to 120 requests and OAuth access tokens to 600 requests over a rolling 60-second period. When Kit returns HTTP 429, Airbyte backs off and retries the request. Use OAuth if your syncs are slow because of rate limiting.

### `purchases` requires OAuth

Kit's List purchases endpoint only accepts OAuth access tokens. If you authenticate with an API key and select the `purchases` stream, the sync fails with an error. Switch to OAuth 2.0 or deselect the `purchases` stream.

### Connections created before version 0.3.0

Versions before 0.3.0 used the Kit V3 API and authenticated with a V3 API secret. Starting with 0.3.0, the connector uses the V4 API. It still falls back to the stored V3 secret if no API key is set, but Kit doesn't accept V3 credentials on the V4 API. If your sync fails with `401 The API key is invalid`, create a V4 API key and enter it under **Authentication Type** > **API Key**.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.3.4 | 2026-10-12 | [88414](https://github.com/airbytehq/airbyte/pull/88414) | Mark `api_secret` as `airbyte_secret` and retitle it Legacy API Secret |
| 0.3.3 | 2025-05-24 | [60414](https://github.com/airbytehq/airbyte/pull/60414) | Update dependencies |
| 0.3.2 | 2025-05-10 | [59955](https://github.com/airbytehq/airbyte/pull/59955) | Update dependencies |
| 0.3.1 | 2025-05-03 | [59410](https://github.com/airbytehq/airbyte/pull/59410) | Update dependencies |
| 0.3.0 | 2025-04-24 | [58617](https://github.com/airbytehq/airbyte/pull/58617) | Update to Kit API v4, add OAuth support, add 8 additional streams, update schemas |
| 0.2.23 | 2025-04-26 | [58849](https://github.com/airbytehq/airbyte/pull/58849) | Update dependencies |
| 0.2.22 | 2025-04-19 | [58341](https://github.com/airbytehq/airbyte/pull/58341) | Update dependencies |
| 0.2.21 | 2025-04-12 | [57808](https://github.com/airbytehq/airbyte/pull/57808) | Update dependencies |
| 0.2.20 | 2025-04-05 | [57198](https://github.com/airbytehq/airbyte/pull/57198) | Update dependencies |
| 0.2.19 | 2025-03-29 | [56524](https://github.com/airbytehq/airbyte/pull/56524) | Update dependencies |
| 0.2.18 | 2025-03-22 | [55951](https://github.com/airbytehq/airbyte/pull/55951) | Update dependencies |
| 0.2.17 | 2025-03-08 | [55270](https://github.com/airbytehq/airbyte/pull/55270) | Update dependencies |
| 0.2.16 | 2025-03-01 | [54976](https://github.com/airbytehq/airbyte/pull/54976) | Update dependencies |
| 0.2.15 | 2025-02-22 | [54379](https://github.com/airbytehq/airbyte/pull/54379) | Update dependencies |
| 0.2.14 | 2025-02-15 | [53751](https://github.com/airbytehq/airbyte/pull/53751) | Update dependencies |
| 0.2.13 | 2025-02-08 | [53342](https://github.com/airbytehq/airbyte/pull/53342) | Update dependencies |
| 0.2.12 | 2025-02-01 | [52823](https://github.com/airbytehq/airbyte/pull/52823) | Update dependencies |
| 0.2.11 | 2025-01-25 | [52332](https://github.com/airbytehq/airbyte/pull/52332) | Update dependencies |
| 0.2.10 | 2025-01-18 | [51673](https://github.com/airbytehq/airbyte/pull/51673) | Update dependencies |
| 0.2.9 | 2025-01-11 | [51107](https://github.com/airbytehq/airbyte/pull/51107) | Update dependencies |
| 0.2.8 | 2024-12-28 | [50522](https://github.com/airbytehq/airbyte/pull/50522) | Update dependencies |
| 0.2.7 | 2024-12-21 | [50066](https://github.com/airbytehq/airbyte/pull/50066) | Update dependencies |
| 0.2.6 | 2024-12-14 | [49510](https://github.com/airbytehq/airbyte/pull/49510) | Update dependencies |
| 0.2.5 | 2024-12-12 | [48958](https://github.com/airbytehq/airbyte/pull/48958) | Update dependencies |
| 0.2.4 | 2024-11-04 | [48217](https://github.com/airbytehq/airbyte/pull/48217) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47764](https://github.com/airbytehq/airbyte/pull/47764) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47619](https://github.com/airbytehq/airbyte/pull/47619) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44161](https://github.com/airbytehq/airbyte/pull/44161) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43803](https://github.com/airbytehq/airbyte/pull/43803) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43503](https://github.com/airbytehq/airbyte/pull/43503) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43237](https://github.com/airbytehq/airbyte/pull/43237) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42643](https://github.com/airbytehq/airbyte/pull/42643) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42363](https://github.com/airbytehq/airbyte/pull/42363) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41742](https://github.com/airbytehq/airbyte/pull/41742) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41405](https://github.com/airbytehq/airbyte/pull/41405) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41272](https://github.com/airbytehq/airbyte/pull/41272) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40860](https://github.com/airbytehq/airbyte/pull/40860) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40282](https://github.com/airbytehq/airbyte/pull/40282) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39989](https://github.com/airbytehq/airbyte/pull/39989) | Update dependencies |
| 0.1.3 | 2024-06-17 | [39505](https://github.com/airbytehq/airbyte/pull/39505) | Make compatible with builder |
| 0.1.2 | 2024-06-06 | [39299](https://github.com/airbytehq/airbyte/pull/39299) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38492](https://github.com/airbytehq/airbyte/pull/38492) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18455](https://github.com/airbytehq/airbyte/pull/18455) | Initial commit |

</details>
