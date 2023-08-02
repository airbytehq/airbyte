# Adjust

The Adjust source connector interacts with the Adjust reports API, which
provides aggregated metrics from various Adjust sources; KPI Service
deliverables, KPI Service cohorts, SKAdNetwork, and Ad Spend.

Metrics and dimensions of interest for a time span are requested from a single
HTTP endpoint by using URL query parameters. The time span (also a query
parameter)can be specified in several ways, but the connector simply
requests daily chunks of data.

Dimensions allow for a breakdown of metrics into groups. For instance by
country and operating system.

[Authentication](https://help.adjust.com/en/article/report-service-api-authentication)
is handled via a regular `Authorization` HTTP header which can be found in the UI.

See the [reports documentation](https://help.adjust.com/en/article/reports-endpoint)
for details on how the API works.
