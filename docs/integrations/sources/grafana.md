# Grafana
Grafana is an observability and analytics platform that lets teams visualize, explore, and alert on their data from dozens of sources in one place. This connector replicates Grafana resources such as datasources, dashboards, folders, and users into your warehouse or lake, so you can audit configuration changes, analyze usage, and join Grafana metadata with the rest of your operational data. By syncing Grafana objects on a schedule, you can track how dashboards evolve over time, understand which teams and visualizations are most active, and build governance and reliability reporting on top of your Grafana estate.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `url` | `string` | Grafana URL. The URL of your Grafana instance (e.g., https://your-grafana.grafana.net) |  |
| `api_key` | `string` | API Key. Grafana API Key or Service Account Token |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| datasources | id | No pagination | ✅ |  ❌  |
| folders | id | No pagination | ✅ |  ❌  |
| dashboards | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| users | userId | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-01-29 | | Initial release by [@tgonzalezc5](https://github.com/tgonzalezc5) via Connector Builder |

</details>
