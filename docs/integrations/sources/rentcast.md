# RentCast
RentCast is the leading rental property analytics, estimation and reporting software .
This connector enables you to extract data from endpoints like Value Estimate , Rent Estimate , Property Records , Sale Listings and Rental Listings
Docs : https://developers.rentcast.io/reference/introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `address` | `string` | Address. The full address of the property, in the format of Street, City, State, Zip. Used to retrieve data for a specific property, or together with the radius parameter to search for listings in a specific area |  |
| `city` | `string` | City. The name of the city, used to search for listings in a specific city. This parameter is case-sensitive |  |
| `state` | `string` | State. The 2-character state abbreviation, used to search for listings in a specific state. This parameter is case-sensitive |  |
| `zipcode` | `string` | Zip Code. The 5-digit zip code, used to search for listings in a specific zip code |  |
| `latitude` | `string` | Latitude. The latitude of the search area. Use the latitude/longitude and radius parameters to search for listings in a specific area |  |
| `longitude` | `string` | Longitude. The longitude of the search area. Use the latitude/longitude and radius parameters to search for listings in a specific area |  |
| `radius` | `string` | Radius. The radius of the search area in miles, with a maximum of 100. Use in combination with the latitude/longitude or address parameters to search for listings in a specific area |  |
| `property_type` | `string` | Property Type. The type of the property, used to search for listings matching this criteria : Single Family , Condo , Townhouse , Manufactured ,  Multi-Family , Apartment , Land , |  |
| `bedrooms` | `number` | Bedrooms. The number of bedrooms, used to search for listings matching this criteria. Use 0 to indicate a studio layout |  |
| `bath_rooms` | `integer` | Bath Rooms. The number of bathrooms, used to search for listings matching this criteria. Supports fractions to indicate partial bathrooms |  |
| `status` | `string` | Status. The current listing status, used to search for listings matching this criteria : Active or Inactive |  |
| `days_old` | `string` | Days Old. The maximum number of days since a property was listed on the market, with a minimum of 1 or The maximum number of days since a property was last sold, with a minimum of 1. Used to search for properties that were sold within the specified date range |  |
| `data_type_` | `string` | Data Type . The type of aggregate market data to return. Defaults to &quot;All&quot; if not provided : All , Sale , Rental |  |
| `history_range` | `string` | History Range. The time range for historical record entries, in months. Defaults to 12 if not provided |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Property Records | id | DefaultPaginator | ✅ |  ❌  |
| Sale Listings | id | DefaultPaginator | ✅ |  ❌  |
| Rental Listings | id | No pagination | ✅ |  ❌  |
| Statistics |  | No pagination | ✅ |  ❌  |
| Value Estimate |  | No pagination | ✅ |  ❌  |
| Rent Estimate |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-01-25 | [52538](https://github.com/airbytehq/airbyte/pull/52538) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51910](https://github.com/airbytehq/airbyte/pull/51910) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51352](https://github.com/airbytehq/airbyte/pull/51352) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50730](https://github.com/airbytehq/airbyte/pull/50730) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50254](https://github.com/airbytehq/airbyte/pull/50254) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49666](https://github.com/airbytehq/airbyte/pull/49666) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49345](https://github.com/airbytehq/airbyte/pull/49345) | Update dependencies |
| 0.0.2 | 2024-12-11 | [47604](https://github.com/airbytehq/airbyte/pull/47604) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-18 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
