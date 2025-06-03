package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.Sql
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.future.await

private val log = KotlinLogging.logger {}

@Singleton
class ClickhouseDatabaseHandler(private val clickhouseClient: Client): DatabaseHandler {
    override fun execute(sql: Sql) {
        val statement =
            java.lang.String.join("\n", sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION"))
        log.error { "Executing SQL: $statement" }
        clickhouseClient.execute(statement).get()
    }

    override suspend fun createNamespaces(namespaces: Collection<String>) {
        log.error { "Namespaces to create: ${namespaces.size}" }
        namespaces.forEach { namespace ->
                log.error { "Ignoring create namespace request for ClickHouse: $namespace" }
            val statement = getDatabaseStatement(namespace)
            clickhouseClient.execute(statement).await()
        }
    }

    private fun getDatabaseStatement(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace` "
    }
}
