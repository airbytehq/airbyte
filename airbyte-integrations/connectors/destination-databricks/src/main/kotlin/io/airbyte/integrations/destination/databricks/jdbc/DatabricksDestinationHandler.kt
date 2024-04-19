package io.airbyte.integrations.destination.databricks.jdbc

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.SQLException
import java.util.*
import org.jooq.SQLDialect

private val log = KotlinLogging.logger {}
class DatabricksDestinationHandler(
    private val databaseName: String,
    private val jdbcDatabase: JdbcDatabase,
    private val rawTableSchemaName: String,
) : DestinationHandler<MinimumDestinationState.Impl> {

    override fun execute(sql: Sql) {
        val transactions: List<List<String>> = sql.transactions
        val queryId = UUID.randomUUID()
        for (transaction in transactions) {
            val transactionId = UUID.randomUUID()
            log.info {
                "Executing sql $queryId-$transactionId: ${transactions.joinToString("\n")}"
            }
            val startTime = System.currentTimeMillis()

            try {
                jdbcDatabase.executeWithinTransaction(transaction)
            } catch (e: SQLException) {
                log.error(e) {
                    "Sql $queryId-$transactionId failed in ${System.currentTimeMillis() - startTime} ms"
                }
                throw e
            }
            log.info {
                "Sql $queryId-$transactionId completed in ${System.currentTimeMillis() - startTime} ms"
            }
        }
    }

    override fun gatherInitialState(streamConfigs: List<StreamConfig>): List<DestinationInitialStatus<MinimumDestinationState.Impl>> {
        TODO("Not yet implemented")
    }

    override fun commitDestinationStates(destinationStates: Map<StreamId, MinimumDestinationState.Impl>) {
        TODO("Not yet implemented")
    }


}
