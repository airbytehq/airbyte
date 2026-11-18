# Reviewflowz

This page contains the setup guide and reference information for the [Reviewflowz](https://www.reviewflowz.com) source connector.

Reviewflowz collects a business's online reviews from 200+ review platforms (Google, Tripadvisor, Trustpilot, Booking.com, the App Store and more) into one account. This connector copies those reviews, the review sources they come from and each source's daily rating history into your destination, through the [Reviewflowz API](https://api.reviewflowz.com/v3/docs).

## Prerequisites

- A Reviewflowz account
- An API key for that account. Only an account admin can create one.

## Setup guide

### Step 1: Create an API key

1. Log in to [Reviewflowz](https://app.reviewflowz.com) as an account admin.
2. Open **Settings → API** and create a **Read only** key.
3. Copy the key now: it starts with `rfz_live_`, and Reviewflowz shows it only once.

A key sees what the person who created it sees, so create it as someone who can see every source you want to copy. See [Authentication](https://api.reviewflowz.com/v3/docs/guides/authentication).

### Step 2: Set up the Reviewflowz connector in Airbyte

1. In Airbyte, go to **Sources** and click **+ New source**.
2. Select **Reviewflowz**.
3. Paste the **API Key**.
4. (Optional) Set the **Lookback Window (days)**. Each incremental sync of `reviews` starts this many days before the last change it saw. The default is 1. Keep it longer than your longest sync.
5. (Optional) Set the **Ratings Start Date** (YYYY-MM-DD), the first day of rating history to copy. The default is two years ago.
6. Click **Set up source**.

## Supported sync modes

| Stream | Full Refresh | Incremental | Primary key | Cursor |
| :-- | :-- | :-- | :-- | :-- |
| `reviews` | Yes | Yes | `root_review` | `updated_at` |
| `sources` | Yes | No | `id` | |
| `ratings_history` | Yes | Yes | `source`, `country`, `period` | `as_of` |

Use **Incremental | Append + Deduped** for `reviews` and `ratings_history`.

## Supported streams

- [`reviews`](https://api.reviewflowz.com/v3/docs/reference/reviews): every review, with its reply, tags, owners and topics. An edited review is a new version with a new `id`; every version shares the `root_review` of the first, so deduplicating on `root_review` keeps one row per review, at its latest version. The first sync copies every review. Later syncs ask for the reviews found, edited, removed, reinstated, replied to, tagged or given an owner since the last change seen, minus the lookback window. A removed review stays, with `removed: true`.
- [`sources`](https://api.reviewflowz.com/v3/docs/reference/sources): the review sources the account follows (a Google business, a Tripadvisor page, an app...), with their current rating. Reviews and ratings point to a source by its `id`.
- [`ratings_history`](https://api.reviewflowz.com/v3/docs/reference/ratings): one row per source and day: the rating, the number of ratings and the new ratings that day, worldwide.

## Limitations

- Incremental syncs of `reviews` don't see a tag or an owner taken off a review, a platform reply that was deleted, or topics found after the review's last change. Run a full refresh now and then to pick those up.
- A review deleted from Reviewflowz (for example when its source is deleted) disappears from the API, and the connector can't tell your destination about it. A full refresh clears it.
- `ratings_history` covers the worldwide rating. Per-country ratings (App Store, Play Store) aren't included.

## Rate limits

The Reviewflowz API answers `429` with a `Retry-After` header when a key goes over its rate limit. The connector waits for that time and retries.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0 | 2026-11-18 | [93971](https://github.com/airbytehq/airbyte/pull/93971) | Initial release |

</details>
