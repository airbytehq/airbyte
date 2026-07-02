# App Store Connection
The App Store Connect app lets you monitor your app&#39;s sales and downloads, reply to App Store Review, get notified of new reviews, respond to reviews, and more.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `iss` | `string` | JWT Payload ISS. The ISS (Issuer) to use for the JWT token |  |
| `kid` | `string` | JWT Header KID. The KID (Key ID) to use for the JWT token |  |
| `vendorID` | `string` | vendorID.  |  |
| `secret_key` | `string` | JWT Secret Key. The secret key to use for the JWT token |  |
| `reviews_start_date` | `string` | Reviews start date.  | 2020-01-01T00:00:00Z |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| list_id_apps |  | DefaultPaginator | ✅ |  ❌  |
| subscriber_report |  | No pagination | ✅ |  ❌  |
| sales_report |  | No pagination | ✅ |  ❌  |
| customer_reviews_per_app | id.app_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-02 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
