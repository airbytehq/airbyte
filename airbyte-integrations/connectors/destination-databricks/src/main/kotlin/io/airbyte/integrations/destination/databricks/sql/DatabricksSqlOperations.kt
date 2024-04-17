package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState

class DatabricksSqlOperations(
    val jdbcDatabase: JdbcDatabase,
    val sqlGenerator: SqlGenerator,
    val destinationHandler: DestinationHandler<MinimumDestinationState.Impl>
) : SqlOperations {

    override fun prepare(streamConfig: StreamConfig): Result<Unit> {
        TODO("Not yet implemented")
    }

    override fun copyIntoTableFromStage(stageId: String, streamId: StreamId): Result<Unit> {
        TODO("Not yet implemented")
    }

    override fun updateFinalTable(streamConfig: StreamConfig): Result<Unit> {
        TODO("Not yet implemented")
    }
}
