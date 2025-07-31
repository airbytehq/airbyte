from collections import Counter

from google.cloud import bigquery

project_id = "airbyte-data-prod"
client = bigquery.Client(project=project_id)

query = """
SELECT
  `airbyte_warehouse.connection_sync`.`workspace_id` AS `workspace_id`,
  DATE_TRUNC(
    `airbyte_warehouse.connection_sync`.`dt`,
    week(sunday)
  ) AS `dt`,
  string_agg(`airbyte_warehouse.connection_sync`.`source_connector_name`, ',') as `sources`
FROM
  `airbyte_warehouse.connection_sync`
WHERE
  (
    `airbyte_warehouse.connection_sync`.`main_failure_origin` = 'source'
  )
  AND `airbyte_warehouse.connection_sync`.`is_cloud` = True
  AND `airbyte_warehouse.connection_sync`.`dt` BETWEEN DATE_TRUNC(DATE_ADD(CURRENT_DATE(), INTERVAL -30 day), day)
  AND DATE_TRUNC(DATE_ADD(CURRENT_DATE(), INTERVAL -1 day), day)
  AND (
    (
      `airbyte_warehouse.connection_sync`.`main_failure_type` <> 'config_error'
    )

    OR (
      `airbyte_warehouse.connection_sync`.`main_failure_type` IS NULL
    )
  )
  AND (
    (
      `airbyte_warehouse.connection_sync`.`main_failure_type` <> 'transient_error'
    )
    OR (
      `airbyte_warehouse.connection_sync`.`main_failure_type` IS NULL
    )
  )
GROUP BY
  `workspace_id`,
  `dt`
ORDER BY
  `workspace_id` ASC,
  `dt` ASC
"""

connectors_per_week = {}

query_job = client.query(query)
rows = query_job.result()
for row in rows:
    connectors_per_week.setdefault(row[1], []).append(frozenset(row[2].split(",")))

for week in sorted(connectors_per_week.keys()):
    print(week)
    print("_________________")
    for sources, count in Counter(connectors_per_week[week]).most_common(10):
        print(f"{sources}, {count}")
    print()
