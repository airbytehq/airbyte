# ShipStation

The ShipStation source connector reads data from the [ShipStation V1 API](https://www.shipstation.com/docs/api/) at `https://ssapi.shipstation.com/`.

## Prerequisites

- A ShipStation account with V1 API access. See ShipStation's [API subscription requirements](https://help.shipstation.com/hc/en-us/articles/360025856212-ShipStation-API) for eligible plans.
- A V1 API key and API secret. Only the ShipStation account owner can generate these credentials, and email verification is required. V2 API keys are not interchangeable with V1 credentials.

## Setup guide

### Get your API credentials

If you already have a valid V1 API key and secret stored securely, use that pair. Otherwise, follow ShipStation's [API key instructions](https://help.shipstation.com/hc/en-us/articles/360025856212-ShipStation-API):

1. Sign in as the ShipStation account owner and open **Settings > Account > API Settings**.
2. Select **V1** from the API version dropdown and click **Generate API Key**.
3. Complete the email verification, then return to generate the key.
4. Choose an expiration period and click **Generate**.
5. Copy the API key and API secret and store them securely. ShipStation displays them only once, immediately after generation.

Before your credentials expire, generate a replacement pair and update the source in Airbyte. See ShipStation's [key rotation instructions](https://help.shipstation.com/hc/en-us/articles/360025856212-ShipStation-API) for details.

### Configure the source in Airbyte

Create a **ShipStation** source and enter the following values:

| Input | Field in Airbyte | Description |
|-------|------------------|-------------|
| `username` | **API Key** | Your ShipStation V1 API key, used as the HTTP Basic authentication username. |
| `password` | **API Secret** | The matching V1 API secret, used as the HTTP Basic authentication password. |
| `start_date` | **Start date** | Required. The starting timestamp for `orders`, `shipments`, and `fulfillments`, in the format `YYYY-MM-DDTHH:mm:ssZ`, for example `2026-01-01T00:00:00Z`. No default value. |

## Supported streams and sync modes

All streams support full refresh. Only `orders`, `shipments`, and `fulfillments` support incremental sync.

| Stream | Data | Primary key | Incremental cursor |
|--------|------|-------------|--------------------|
| `carriers` | Shipping providers connected to your account | `shippingProviderId` | Not supported |
| `carrier_packages` | Package types available for each connected carrier | `carrierCode`, `code` | Not supported |
| `carrier_services` | Shipping services available for each connected carrier | `carrierCode`, `code`, `domestic`, `international` | Not supported |
| `customers` | Customer records | `customerId` | Not supported |
| `fulfillments` | Fulfillment records, including orders marked as shipped through the UI or API | `fulfillmentId` | `createDate` |
| `orders` | Orders | `orderId` | `modifyDate` |
| `products` | Product records | `productId` | Not supported |
| `shipments` | Shipments with labels generated in ShipStation, including shipment items | `shipmentId` | `createDate` |
| `marketplaces` | Supported marketplaces | `name`, `marketplaceId` | Not supported |
| `stores` | Stores, including inactive stores | `storeId` | Not supported |
| `tags` | Tags defined for your account | `tagId` | Not supported |
| `users` | Users, including inactive users | `userId` | Not supported |
| `warehouses` | Ship From locations | `warehouseId` | Not supported |
| `webhooks` | Registered webhook configurations | `WebHookID` | Not supported |

The `carrier_packages` and `carrier_services` streams read the carrier list and request packages or services for each distinct carrier code. You do not need to enter carrier codes manually.

### Incremental sync behavior

- `orders` uses `modifyDate` to retrieve new and updated orders from the configured start date.
- `shipments` and `fulfillments` use `createDate`. Changes to records created before the saved cursor's lookback window are not captured by incremental sync. Use a full refresh to retrieve those changes, with a start date early enough to include the records.
- All three incremental streams use a six-hour lookback window, so subsequent syncs can emit records that were already read.

ShipStation's [V1 API timestamps](https://www.shipstation.com/docs/api/requirements/) use Pacific Time (PST/PDT).

### Shipment coverage

The [`shipments` endpoint](https://www.shipstation.com/docs/api/shipments/list/) returns only shipments with labels generated in ShipStation. Orders marked as shipped through the UI or API are treated as external shipments and are available from the [`fulfillments` endpoint](https://docs.shipstation.com/apis/shipstation-v1/openapi/fulfillments/list_fulfillments).

The `webhooks` stream reads webhook configurations; it does not receive webhook events.

## Rate limits and troubleshooting

ShipStation's [V1 API rate limit](https://www.shipstation.com/docs/api/requirements/) is 40 requests per minute per API key and secret pair. Other applications using the same credentials share this limit. The connector waits according to the `X-Rate-Limit-Reset` response header when rate limited.

- **401 Unauthorized**: Check that the API key and secret are a matching, unexpired V1 pair.
- **402 response**: Check that your ShipStation plan includes V1 API access.
- **429 Too Many Requests**: Reduce overlapping API activity that uses the same credentials if throttling persists.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.3.0 | 2026-11-11 | [91538](https://github.com/airbytehq/airbyte/pull/91538) | Add `tags`, `carrier_packages` and `carrier_services` streams, declare additional `orders`, `products` and `fulfillments` fields, and set heartbeat and suggested-streams metadata |
| 0.2.54 | 2026-11-10 | [91707](https://github.com/airbytehq/airbyte/pull/91707) | Update dependencies |
| 0.2.53 | 2026-11-04 | [90360](https://github.com/airbytehq/airbyte/pull/90360) | Simplify rate-limit error handling configuration with no change in retry behavior |
| 0.2.52 | 2026-11-03 | [90739](https://github.com/airbytehq/airbyte/pull/90739) | Update dependencies |
| 0.2.51 | 2026-10-20 | [89386](https://github.com/airbytehq/airbyte/pull/89386) | Update dependencies |
| 0.2.50 | 2026-10-13 | [88800](https://github.com/airbytehq/airbyte/pull/88800) | Update dependencies |
| 0.2.49 | 2026-10-06 | [88037](https://github.com/airbytehq/airbyte/pull/88037) | Update dependencies |
| 0.2.48 | 2026-09-29 | [87343](https://github.com/airbytehq/airbyte/pull/87343) | Update dependencies |
| 0.2.47 | 2026-09-22 | [86788](https://github.com/airbytehq/airbyte/pull/86788) | Update dependencies |
| 0.2.46 | 2026-09-15 | [86217](https://github.com/airbytehq/airbyte/pull/86217) | Update dependencies |
| 0.2.45 | 2026-09-08 | [85663](https://github.com/airbytehq/airbyte/pull/85663) | Update dependencies |
| 0.2.44 | 2026-08-18 | [84755](https://github.com/airbytehq/airbyte/pull/84755) | Update dependencies |
| 0.2.43 | 2026-08-11 | [84092](https://github.com/airbytehq/airbyte/pull/84092) | Update dependencies |
| 0.2.42 | 2026-08-04 | [83616](https://github.com/airbytehq/airbyte/pull/83616) | Update dependencies |
| 0.2.41 | 2026-07-28 | [83075](https://github.com/airbytehq/airbyte/pull/83075) | Update dependencies |
| 0.2.40 | 2026-07-21 | [82571](https://github.com/airbytehq/airbyte/pull/82571) | Update dependencies |
| 0.2.39 | 2026-07-14 | [82005](https://github.com/airbytehq/airbyte/pull/82005) | Update dependencies |
| 0.2.38 | 2026-06-30 | [81250](https://github.com/airbytehq/airbyte/pull/81250) | Update dependencies |
| 0.2.37 | 2026-06-23 | [80626](https://github.com/airbytehq/airbyte/pull/80626) | Update dependencies |
| 0.2.36 | 2026-06-16 | [80018](https://github.com/airbytehq/airbyte/pull/80018) | Update dependencies |
| 0.2.35 | 2026-06-09 | [79471](https://github.com/airbytehq/airbyte/pull/79471) | Update dependencies |
| 0.2.34 | 2026-06-02 | [78974](https://github.com/airbytehq/airbyte/pull/78974) | Update dependencies |
| 0.2.33 | 2026-04-28 | [77448](https://github.com/airbytehq/airbyte/pull/77448) | Update dependencies |
| 0.2.32 | 2026-04-21 | [75332](https://github.com/airbytehq/airbyte/pull/75332) | Update dependencies |
| 0.2.31 | 2026-03-10 | [74592](https://github.com/airbytehq/airbyte/pull/74592) | Update dependencies |
| 0.2.30 | 2026-02-24 | [73945](https://github.com/airbytehq/airbyte/pull/73945) | Update dependencies |
| 0.2.29 | 2026-02-17 | [73523](https://github.com/airbytehq/airbyte/pull/73523) | Update dependencies |
| 0.2.28 | 2026-02-10 | [73202](https://github.com/airbytehq/airbyte/pull/73202) | Update dependencies |
| 0.2.27 | 2026-02-03 | [72729](https://github.com/airbytehq/airbyte/pull/72729) | Update dependencies |
| 0.2.26 | 2026-01-20 | [72120](https://github.com/airbytehq/airbyte/pull/72120) | Update dependencies |
| 0.2.25 | 2026-01-14 | [71622](https://github.com/airbytehq/airbyte/pull/71622) | Update dependencies |
| 0.2.24 | 2025-12-18 | [70674](https://github.com/airbytehq/airbyte/pull/70674) | Update dependencies |
| 0.2.23 | 2025-11-25 | [70104](https://github.com/airbytehq/airbyte/pull/70104) | Update dependencies |
| 0.2.22 | 2025-11-18 | [69458](https://github.com/airbytehq/airbyte/pull/69458) | Update dependencies |
| 0.2.21 | 2025-10-29 | [68802](https://github.com/airbytehq/airbyte/pull/68802) | Update dependencies |
| 0.2.20 | 2025-10-21 | [68230](https://github.com/airbytehq/airbyte/pull/68230) | Update dependencies |
| 0.2.19 | 2025-10-14 | [67777](https://github.com/airbytehq/airbyte/pull/67777) | Update dependencies |
| 0.2.18 | 2025-10-07 | [67430](https://github.com/airbytehq/airbyte/pull/67430) | Update dependencies |
| 0.2.17 | 2025-09-30 | [66910](https://github.com/airbytehq/airbyte/pull/66910) | Update dependencies |
| 0.2.16 | 2025-09-24 | [66256](https://github.com/airbytehq/airbyte/pull/66256) | Update dependencies |
| 0.2.15 | 2025-09-09 | [65722](https://github.com/airbytehq/airbyte/pull/65722) | Update dependencies |
| 0.2.14 | 2025-08-24 | [65449](https://github.com/airbytehq/airbyte/pull/65449) | Update dependencies |
| 0.2.13 | 2025-08-16 | [64998](https://github.com/airbytehq/airbyte/pull/64998) | Update dependencies |
| 0.2.12 | 2025-08-03 | [64478](https://github.com/airbytehq/airbyte/pull/64478) | Update dependencies |
| 0.2.11 | 2025-07-19 | [63634](https://github.com/airbytehq/airbyte/pull/63634) | Update dependencies |
| 0.2.10 | 2025-07-05 | [62735](https://github.com/airbytehq/airbyte/pull/62735) | Update dependencies |
| 0.2.9 | 2025-06-28 | [62253](https://github.com/airbytehq/airbyte/pull/62253) | Update dependencies |
| 0.2.8 | 2025-06-14 | [61308](https://github.com/airbytehq/airbyte/pull/61308) | Update dependencies |
| 0.2.7 | 2025-05-24 | [60504](https://github.com/airbytehq/airbyte/pull/60504) | Update dependencies |
| 0.2.6 | 2025-05-10 | [60142](https://github.com/airbytehq/airbyte/pull/60142) | Update dependencies |
| 0.2.5 | 2025-05-04 | [59604](https://github.com/airbytehq/airbyte/pull/59604) | Update dependencies |
| 0.2.4 | 2025-04-27 | [59020](https://github.com/airbytehq/airbyte/pull/59020) | Update dependencies |
| 0.2.3 | 2025-04-19 | [57453](https://github.com/airbytehq/airbyte/pull/57453) | Update dependencies |
| 0.2.2 | 2025-03-29 | [56874](https://github.com/airbytehq/airbyte/pull/56874) | Update dependencies |
| 0.2.1 | 2025-03-22 | [56257](https://github.com/airbytehq/airbyte/pull/56257) | Update dependencies |
| 0.2.0 | 2025-03-13 | [55738](https://github.com/airbytehq/airbyte/pull/55738) | add incremental for orders, shipments and fullfillments |
| 0.1.5 | 2025-03-09 | [55648](https://github.com/airbytehq/airbyte/pull/55648) | Update dependencies |
| 0.1.4 | 2025-03-01 | [55122](https://github.com/airbytehq/airbyte/pull/55122) | Update dependencies |
| 0.1.3 | 2025-02-22 | [54511](https://github.com/airbytehq/airbyte/pull/54511) | Update dependencies |
| 0.1.2 | 2025-02-15 | [54047](https://github.com/airbytehq/airbyte/pull/54047) | Update dependencies |
| 0.1.1 | 2025-02-08 | [53551](https://github.com/airbytehq/airbyte/pull/53551) | Update dependencies |
| 0.1.0 | 2025-02-03 | [52707](https://github.com/airbytehq/airbyte/pull/52707) | Change auth method |
| 0.0.6 | 2025-02-01 | [53109](https://github.com/airbytehq/airbyte/pull/53109) | Update dependencies |
| 0.0.5 | 2025-01-25 | [52405](https://github.com/airbytehq/airbyte/pull/52405) | Update dependencies |
| 0.0.4 | 2025-01-18 | [51911](https://github.com/airbytehq/airbyte/pull/51911) | Update dependencies |
| 0.0.3 | 2025-01-11 | [51328](https://github.com/airbytehq/airbyte/pull/51328) | Update dependencies |
| 0.0.2 | 2024-12-28 | [50726](https://github.com/airbytehq/airbyte/pull/50726) | Update dependencies |
| 0.0.1 | 2024-12-21 | | Initial release by [@JohnnyRafael](https://github.com/JohnnyRafael) via Connector Builder |

</details>
