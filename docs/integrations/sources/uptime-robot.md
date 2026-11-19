# UptimeRobot

Sync your [UptimeRobot](https://uptimerobot.com/) monitors into your data warehouse.
This source connector syncs every monitor in your account, including its configuration, current status, average response time, recent response times and up/down event logs.
It uses the [UptimeRobot API v2](https://uptimerobot.com/api/). Configuration requires only your UptimeRobot API key.

## Prerequisites

- An UptimeRobot account
- An UptimeRobot **Main API Key** or **Read-Only API Key**. In the UptimeRobot dashboard, go to **Integrations & API** > **API** to create or copy one. A read-only key is enough for this connector.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your UptimeRobot Main API Key or Read-Only API Key. |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| monitors | id | DefaultPaginator | ✅ | ❌ |

## Limitations

- The UptimeRobot API returns up to 50 monitors per request. The connector pages through all of them using `offset` and `limit`.
- For security, the connector drops each monitor's `http_username` and `http_password` (the HTTP basic-auth credentials a monitor uses to check your site), so they are never written to your destination.
- UptimeRobot applies [rate limits](https://uptimerobot.com/api/#rate-limits) based on your plan.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2026-11-19 | | Initial release via Connector Builder |

</details>
