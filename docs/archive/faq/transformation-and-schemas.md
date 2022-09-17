# Transformation and Schemas

## **Where's the T in Airbyte’s ETL tool?**

Airbyte is actually an ELT tool, and you have the freedom to use it as an EL-only tool. The transformation part is done by default, but it is optional. You can choose to receive the data in raw \(JSON file for instance\) in your destination.

We do provide normalization \(if option is still on\) so that data analysts / scientists / any users of the data can use it without much effort.

We also intend to integrate deeply with dbt to make it easier for your team to continue relying you on them, if this was what you were doing.

## **How does Airbyte handle replication when a data source changes its schema?**

Airbyte continues to sync data using the configured schema until that schema is updated. Because Airbyte treats all fields as optional, if a field is renamed or deleted in the source, that field simply will no longer be replicated, but all remaining fields will. The same is true for streams as well.

For now, the schema can only be updated manually in the UI \(by clicking "Update Schema" in the settings page for the connection\). When a schema is updated Airbyte will re-sync all data for that source using the new schema.

## **How does Airbyte handle namespaces \(or schemas for the DB-inclined\)?**

Airbyte respects source-defined namespaces when syncing data with a namespace-supported destination. See [this](../../understanding-airbyte/namespaces.md) for more details.

