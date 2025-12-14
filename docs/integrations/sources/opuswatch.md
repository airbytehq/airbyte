# OPUSWatch
## Unlock Horticultural Insights with Airbyte and OPUSWatch

**What is OPUSWatch?**
OPUSWatch is a smart wearable solution developed by OPUS Solutions B.V., based in the Netherlands. This innovative smartwatch is specifically designed for the horticulture industry to digitize and streamline various operational processes within greenhouses and nurseries. It empowers growers to gain real-time insights into their labor, productivity, and overall operations. Employees use the OPUSWatch to easily record their tasks, track their work on specific crops, and even manage orders directly from their wrist. This data is then fed into a central system for analysis and decision-making.

Website: opuswatch.nl

**What does the OPUSWatch Airbyte Connector do?**
The Airbyte connector for OPUSWatch allows you to seamlessly extract valuable data from the OPUSWatch platform and load it into your data warehouse or lake. By connecting OPUSWatch to Airbyte, you can centralize your horticultural operational data with other business-critical information, enabling comprehensive analysis and reporting.

**With the OPUSWatch Airbyte connector, you can retrieve the following streams of data:**
* **Clients:** Information about your clients or customers.
* **Locations:** Details about the different locations or areas within your greenhouse or nursery.
* **Rows:** Data pertaining to the specific rows or sections where plants are cultivated.
* **Users:** Information about the individuals who have access to the OPUSWatch system.
* **Workers:** Details about your workforce, including their identification and potentially other relevant attributes.
* **Worker Groups:** Information about how your workers are organized into teams or groups.
* **Tasks:** Data on the various activities or jobs that are performed by workers.
* **Task Groups:** Information about how tasks are categorized or grouped together.
* **Labels:** Details about the different labels used for plants, products, or processes.
* **Varieties:** Information on the different plant varieties being cultivated.
* **Registrations Initial:** A snapshot of initial work registrations recorded by the OPUSWatch devices.
* **Registrations Incremental:** Updates and new work registrations recorded by the OPUSWatch devices since the last synchronization.
* **Sessions Initial:** A snapshot of initial work sessions or periods tracked by the OPUSWatch devices.
* **Sessions Incremental:** Updates and new work sessions or periods tracked by the OPUSWatch devices since the last synchronization.

By leveraging the OPUSWatch Airbyte connector, horticultural businesses can break down data silos and gain a holistic view of their operations. This enables data-driven decision-making for optimizing labor allocation, improving productivity, and ultimately enhancing the efficiency of their greenhouse or nursery operations.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date.  | 20250101 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| client |  | No pagination | ✅ |  ❌  |
| locations |  | No pagination | ✅ |  ❌  |
| rows |  | No pagination | ✅ |  ❌  |
| users |  | No pagination | ✅ |  ❌  |
| workers |  | No pagination | ✅ |  ❌  |
| worker groups |  | No pagination | ✅ |  ❌  |
| tasks |  | No pagination | ✅ |  ❌  |
| task groups |  | No pagination | ✅ |  ❌  |
| labels |  | No pagination | ✅ |  ❌  |
| varieties |  | No pagination | ✅ |  ❌  |
| registrations initial |  | DefaultPaginator | ✅ |  ❌  |
| registrations incremental |  | No pagination | ✅ |  ❌  |
| sessions initial |  | DefaultPaginator | ✅ |  ❌  |
| sessions incremental |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.21 | 2025-12-09 | [70518](https://github.com/airbytehq/airbyte/pull/70518) | Update dependencies |
| 0.0.20 | 2025-11-25 | [70113](https://github.com/airbytehq/airbyte/pull/70113) | Update dependencies |
| 0.0.19 | 2025-11-18 | [69702](https://github.com/airbytehq/airbyte/pull/69702) | Update dependencies |
| 0.0.18 | 2025-10-29 | [69035](https://github.com/airbytehq/airbyte/pull/69035) | Update dependencies |
| 0.0.17 | 2025-10-21 | [68323](https://github.com/airbytehq/airbyte/pull/68323) | Update dependencies |
| 0.0.16 | 2025-10-14 | [67804](https://github.com/airbytehq/airbyte/pull/67804) | Update dependencies |
| 0.0.15 | 2025-10-07 | [67347](https://github.com/airbytehq/airbyte/pull/67347) | Update dependencies |
| 0.0.14 | 2025-09-30 | [66379](https://github.com/airbytehq/airbyte/pull/66379) | Update dependencies |
| 0.0.13 | 2025-09-09 | [65891](https://github.com/airbytehq/airbyte/pull/65891) | Update dependencies |
| 0.0.12 | 2025-08-23 | [65199](https://github.com/airbytehq/airbyte/pull/65199) | Update dependencies |
| 0.0.11 | 2025-08-09 | [64781](https://github.com/airbytehq/airbyte/pull/64781) | Update dependencies |
| 0.0.10 | 2025-08-02 | [64205](https://github.com/airbytehq/airbyte/pull/64205) | Update dependencies |
| 0.0.9 | 2025-07-26 | [63856](https://github.com/airbytehq/airbyte/pull/63856) | Update dependencies |
| 0.0.8 | 2025-07-19 | [63393](https://github.com/airbytehq/airbyte/pull/63393) | Update dependencies |
| 0.0.7 | 2025-07-12 | [63184](https://github.com/airbytehq/airbyte/pull/63184) | Update dependencies |
| 0.0.6 | 2025-07-05 | [62574](https://github.com/airbytehq/airbyte/pull/62574) | Update dependencies |
| 0.0.5 | 2025-06-28 | [62391](https://github.com/airbytehq/airbyte/pull/62391) | Update dependencies |
| 0.0.4 | 2025-06-21 | [60559](https://github.com/airbytehq/airbyte/pull/60559) | Update dependencies |
| 0.0.3 | 2025-05-10 | [60190](https://github.com/airbytehq/airbyte/pull/60190) | Update dependencies |
| 0.0.2 | 2025-05-04 | [59519](https://github.com/airbytehq/airbyte/pull/59519) | Update dependencies |
| 0.0.1 | 2025-04-22 | | Initial release by [@SebasZwinkels](https://github.com/SebasZwinkels) via Connector Builder |

</details>
