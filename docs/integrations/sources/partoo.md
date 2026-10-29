# Partoo

This page contains the setup guide and reference information for the [Partoo](https://www.partoo.co) source connector.

Partoo is a local marketing platform for multi-location businesses: it manages business listings, customer reviews, messaging, posts and customer feedback across Google, Facebook and other publishers. This connector replicates that data, plus Google Business Profile and review analytics, from the [Partoo REST API v2](https://developers.partoo.co).

## Prerequisites

- A Partoo account
- A Partoo API key. Ask your Partoo Account Manager for one. The key only sees the businesses and data its user can access, so use a key for a user with access to everything you want to sync.

## Setup guide

### Step 1: Get an API key

Contact your Partoo Account Manager and ask for an API key for the environment you want to sync:

- **Production** for your live data.
- **Sandbox** for testing. The sandbox starts empty and has no reviews or analytics data.

### Step 2: Set up the Partoo connector in Airbyte

1. In Airbyte, go to **Sources** and click **New source**.
2. Search for and select **Partoo**.
3. Enter your **API Key**.
4. Enter a **Start Date** in `YYYY-MM-DDTHH:MM:SSZ` format. Incremental streams replicate data from this date.
5. Choose the **Environment**: `production` (default) or `sandbox`.
6. Click **Set up source**. Airbyte checks the key by listing your businesses.

## Supported sync modes

| Stream                   | Full Refresh | Incremental |
| :----------------------- | :----------- | :---------- |
| `businesses`             | Yes          | Yes         |
| `reviews`                | Yes          | Yes         |
| `conversations`          | Yes          | Yes         |
| `messages`               | Yes          | Yes         |
| `posts`                  | Yes          | No          |
| `users`                  | Yes          | No          |
| `organizations`          | Yes          | No          |
| `feedback_forms`         | Yes          | No          |
| `feedback_results`       | Yes          | Yes         |
| `presence_metrics_daily` | Yes          | Yes         |
| `review_metrics_daily`   | Yes          | Yes         |

## Supported streams

| Stream                   | Endpoint                          | Primary key          | Description                                                                                       |
| :----------------------- | :-------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------ |
| `businesses`             | `GET /business/search`            | `id`                 | Business locations and their listing data. Incremental on `modified`.                             |
| `reviews`                | `GET /reviews`                    | `id`                 | Customer reviews from Google, Facebook, Tripadvisor and other partners. Incremental on `update_date`. |
| `conversations`          | `GET /conversations`              | `id`                 | Messaging conversations. Incremental on `last_message_date`.                                      |
| `messages`               | `GET /messages`                   | `id`                 | Messages of each conversation. Incremental on `date`.                                             |
| `posts`                  | `GET /posts`                      | `id`                 | Posts published to Google and other publishers.                                                   |
| `users`                  | `GET /user/search`                | `id`                 | Partoo users, their roles and the businesses assigned to them.                                    |
| `organizations`          | `GET /org/search`                 | `org_id`             | Organizations visible to the API key.                                                             |
| `feedback_forms`         | `GET /feedback/feedback_form`     | `id`                 | Customer feedback forms.                                                                          |
| `feedback_results`       | `GET /feedback/feedback_result`   | `id`                 | Answers to feedback forms, including NPS. Incremental on `created`.                               |
| `presence_metrics_daily` | `GET /presence_analytics/metrics` | `business_id`, `date` | Google Business Profile impressions, calls, direction requests and website clicks per business per day. |
| `review_metrics_daily`   | `GET /review_analytics/metrics`   | `business_id`, `date` | Review metrics per business per day: average rating, review count, rating distribution, reply time and reply method. |

### Notes on streams

- `messages`: each sync re-reads only the conversations whose `last_message_date` changed since the previous sync, then keeps the messages newer than the saved state.
- `presence_metrics_daily`: Google revises its figures for the last 5 days, so each sync re-reads the last 7 days.
- `review_metrics_daily`: the Partoo API groups review metrics by one dimension at a time, so the connector requests per-business metrics one day at a time and adds the `date`. The day filter applies to the review's update date, so a day's figures cover the reviews updated that day.
- `presence_metrics_daily` only returns data for businesses subscribed to Presence Management, and `review_metrics_daily` for businesses subscribed to Review Management.
- `feedback_forms` and `feedback_results` use Partoo's Feedback Management API, which Partoo labels as beta.
- `users` contains user names and email addresses.

## Performance considerations

Partoo allows 300 API requests per minute per organization. The connector stays under 280 requests per minute and, on HTTP 429, waits for the time given in the `Retry-After` header before retrying. `review_metrics_daily` makes at least one request per day of history, so a first sync with an early start date takes longer. To raise the limit, contact your Partoo Customer Success Manager.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2026-10-29 | [90178](https://github.com/airbytehq/airbyte/pull/90178) | Initial release |

</details>
