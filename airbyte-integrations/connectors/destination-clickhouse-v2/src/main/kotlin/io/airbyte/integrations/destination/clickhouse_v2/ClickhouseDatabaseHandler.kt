package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.Sql
import jakarta.inject.Singleton

@Singleton
class ClickhouseDatabaseHandler(private val clickhouseClient: Client): DatabaseHandler {
    override fun execute(sql: Sql) {
        val statement = java.lang.String.join("\n", sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION"))

        clickhouseClient.execute(statement)
    }

    override suspend fun createNamespaces(namespaces: Collection<String>) {
    }
}
