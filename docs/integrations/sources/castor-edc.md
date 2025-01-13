# Castor EDC
This document provides the specifications of the [`source-castor-edc`](https://uk.castoredc.com/api#/), describing the currently available
API endpoints and methods. 

Documentation: https://uk.castoredc.com/api#/

## Authentication
Visit `https://YOUR_REGION.castoredc.com/account/settings` for getting your client id and secret

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `url_region` | `string` | URL Region. The url region given at time of registration | uk |
| `client_id` | `string` | Client ID. Visit `https://YOUR_REGION.castoredc.com/account/settings` |  |
| `client_secret` | `string` | Client secret. Visit `https://YOUR_REGION.castoredc.com/account/settings` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| user | id | No pagination | ✅ |  ✅  |
| study | crf_id | DefaultPaginator | ✅ |  ✅  |
| audit_trial | uuid | DefaultPaginator | ✅ |  ✅  |
| country | id | No pagination | ✅ |  ❌  |
| study_survey | id | DefaultPaginator | ✅ |  ❌  |
| study_survey_package | id | DefaultPaginator | ✅ |  ❌  |
| study_site | id | DefaultPaginator | ✅ |  ❌  |
| study_fields | id | DefaultPaginator | ✅ |  ❌  |
| study_field_dependency | id | DefaultPaginator | ✅ |  ❌  |
| study_field_validation | id | DefaultPaginator | ✅ |  ❌  |
| study_form | id | DefaultPaginator | ✅ |  ❌  |
| study_role | uuid | DefaultPaginator | ✅ |  ❌  |
| study_fieldoption_groups | id | DefaultPaginator | ✅ |  ❌  |
| study_statistics | study_id | DefaultPaginator | ✅ |  ❌  |
| study_user | id | DefaultPaginator | ✅ |  ✅  |
| study_visit | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-01-11 | [51244](https://github.com/airbytehq/airbyte/pull/51244) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50456](https://github.com/airbytehq/airbyte/pull/50456) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50156](https://github.com/airbytehq/airbyte/pull/50156) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49591](https://github.com/airbytehq/airbyte/pull/49591) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49289](https://github.com/airbytehq/airbyte/pull/49289) | Update dependencies |
| 0.0.5 | 2024-12-11 | [49019](https://github.com/airbytehq/airbyte/pull/49019) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48298](https://github.com/airbytehq/airbyte/pull/48298) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47741](https://github.com/airbytehq/airbyte/pull/47741) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47644](https://github.com/airbytehq/airbyte/pull/47644) | Update dependencies |
| 0.0.1 | 2024-10-12 | [46759](https://github.com/airbytehq/airbyte/pull/46759) | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
