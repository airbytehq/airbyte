package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.Sql
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
class ClickhouseDatabaseHandler(private val clickhouseClient: Client): DatabaseHandler {
    override fun execute(sql: Sql) {
        val statement =
            java.lang.String.join("\n", sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION"))
        log.error { "Executing SQL: $statement" }
        clickhouseClient.execute(statement)
    }

    override suspend fun createNamespaces(namespaces: Collection<String>) {
        namespaces.forEach { namespace ->
            {
                // ClickHouse does not have a concept of namespaces, so we can ignore this.
                log.info { "Ignoring create namespace request for ClickHouse: $namespace" }
            }
        }
    }
}
