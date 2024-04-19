package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import org.jooq.SQLDialect

class DatabricksDestinationHandler(
    databaseName: String,
    jdbcDatabase: JdbcDatabase,
    rawTableSchemaName: String,
    dialect: SQLDialect,
) : JdbcDestinationHandler<MinimumDestinationState>(
    databaseName,
    jdbcDatabase,
    rawTableSchemaName,
    dialect,
) {
    override fun toJdbcTypeName(airbyteType: AirbyteType?): String {
        TODO("Not yet implemented")
    }

    override fun toDestinationState(json: JsonNode?): MinimumDestinationState {
        TODO("Not yet implemented")
    }

}
