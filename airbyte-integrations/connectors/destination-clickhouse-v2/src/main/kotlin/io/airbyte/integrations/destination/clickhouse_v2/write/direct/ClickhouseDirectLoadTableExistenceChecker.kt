package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.migrations.DirectLoadTableExistenceChecker
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoadTableExistenceChecker(private val client: Client):
    DirectLoadTableExistenceChecker {
    override fun listExistingTables(tables: Collection<TableName>): Collection<TableName> =
        tables.filter {
            try {
                client.getTableSchema(it.name) != null
            } catch (e: Exception) {
                // If an exception occurs, we assume the table does not exist.
                false
            }
        }
}
