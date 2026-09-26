# TikTok Organic source connector

This connector syncs **TikTok Business (Organic)** analytics via the TikTok Business API.

## Prerequisites

- A TikTok developer app with **Client Key** and **Client Secret**
- A valid **Refresh Token** (OAuth)
- Your **Open ID / Business ID**

## Configuration

- `client_key` (required, secret): TikTok app client key
- `client_secret` (required, secret): TikTok app client secret
- `refresh_token` (required, secret): OAuth refresh token
- `open_id` (required): TikTok Business Account ID (Open ID)
- `start_date` (optional): `YYYY-MM-DD` (defaults to 30 days ago)

## Streams

- `business_user`: Daily account metrics
- `business_videos`: Video-level metrics (paginated via `cursor`)

## Notes

- TikTok endpoints expect `YYYY-MM-DD` date filters; the connector normalizes timestamp-like values down to a date.
- For `business_user`, records are keyed by `date` and deduplicated within a slice.
