# DrChrono
Extracts healthcare data from DrChrono EHR including patients, appointments, clinical notes, medications, allergies, problems, vitals, and billing information. Supports incremental sync with configurable date.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. Get this by running the refresh script (valid for 10 hours) |  |
| `start_date` | `string` | Start Date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| patients | id | DefaultPaginator | ✅ |  ✅  |
| appointments | id | DefaultPaginator | ✅ |  ✅  |
| clinical_notes | id | DefaultPaginator | ✅ |  ✅  |
| medications | id | DefaultPaginator | ✅ |  ✅  |
| allergies | id | DefaultPaginator | ✅ |  ✅  |
| problems | id | DefaultPaginator | ✅ |  ✅  |
| doctors | id | DefaultPaginator | ✅ |  ✅  |
| vitals | id | DefaultPaginator | ✅ |  ❌  |
| offices | id | DefaultPaginator | ✅ |  ❌  |
| patient_flag_types | id | DefaultPaginator | ✅ |  ❌  |
| appointment_templates | id | DefaultPaginator | ✅ |  ❌  |
| clinical_note_templates | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| billing_profiles | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-12-25 | | Initial release by [@khusa71](https://github.com/khusa71) via Connector Builder |

</details>
