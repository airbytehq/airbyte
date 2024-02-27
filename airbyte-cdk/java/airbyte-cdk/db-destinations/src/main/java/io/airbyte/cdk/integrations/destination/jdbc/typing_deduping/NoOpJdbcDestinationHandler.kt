package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialState
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig

class NoOpJdbcDestinationHandler(databaseName: String,
                                 jdbcDatabase: JdbcDatabase
): JdbcDestinationHandler(databaseName, jdbcDatabase) {
    override fun execute(sql: Sql?) {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun gatherInitialState(streamConfigs: MutableList<StreamConfig>?): MutableList<DestinationInitialState> {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun existingSchemaMatchesStreamConfig(
        stream: StreamConfig?,
        existingTable: TableDefinition?
    ): Boolean {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun toJdbcTypeName(airbyteType: AirbyteType?): String {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }
}
