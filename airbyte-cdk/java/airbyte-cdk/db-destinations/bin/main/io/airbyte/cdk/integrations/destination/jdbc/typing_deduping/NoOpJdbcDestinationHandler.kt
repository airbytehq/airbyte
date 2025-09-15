/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import org.jooq.SQLDialect

class NoOpJdbcDestinationHandler<DestinationState>(
    databaseName: String?,
    jdbcDatabase: JdbcDatabase,
    rawTableSchemaName: String,
    sqlDialect: SQLDialect,
    generationHandler: JdbcGenerationHandler,
) :
    JdbcDestinationHandler<DestinationState>(
        databaseName,
        jdbcDatabase,
        rawTableSchemaName,
        sqlDialect,
        generationHandler = generationHandler,
    ) {

    override fun execute(sql: Sql) {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun gatherInitialState(
        streamConfigs: List<StreamConfig>
    ): List<DestinationInitialStatus<DestinationState>> {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun commitDestinationStates(destinationStates: Map<StreamId, DestinationState>) {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun toDestinationState(json: JsonNode): DestinationState {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun createNamespaces(schemas: Set<String>) {
        // Empty op, not used in old code.
    }

    override fun toJdbcTypeName(airbyteType: AirbyteType): String {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }
}
