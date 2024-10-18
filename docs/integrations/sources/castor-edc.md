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
| 0.0.1 | 2024-10-12 | [46759](https://github.com/airbytehq/airbyte/pull/46759) | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
