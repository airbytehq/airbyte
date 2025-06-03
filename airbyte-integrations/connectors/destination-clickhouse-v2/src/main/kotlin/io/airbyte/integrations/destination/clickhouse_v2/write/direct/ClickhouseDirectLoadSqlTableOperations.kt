package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseDatabaseHandler

class ClickhouseDirectLoadSqlTableOperations(
    private val client: Client,
    sqlGenerator: ClickhouseDirectLoadSqlGenerator,
    destinationHandler: ClickhouseDatabaseHandler,
) : DefaultDirectLoadTableSqlOperations(sqlGenerator, destinationHandler) {
    override fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // manually delete the target table - otherwise we can't e.g. update the partitioning scheme
        client.execute(
            "DROP TABLE IF EXISTS `${targetTableName.name}`"
        ).get()

        // Run the ALTER TABLE RENAME TO statement to move the table.
        client.execute(
            "ALTER TABLE `${sourceTableName.name}` RENAME TO `${targetTableName.name}`"
        ).get()
    }
}
