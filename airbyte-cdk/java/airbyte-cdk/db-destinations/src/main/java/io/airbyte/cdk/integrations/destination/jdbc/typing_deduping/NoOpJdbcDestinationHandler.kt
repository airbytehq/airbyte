/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import org.jooq.SQLDialect

class NoOpJdbcDestinationHandler<DestinationState>(
    databaseName: String,
    jdbcDatabase: JdbcDatabase,
    rawTableSchemaName: String,
    sqlDialect: SQLDialect
) :
    JdbcDestinationHandler<DestinationState>(
        databaseName,
        jdbcDatabase,
        rawTableSchemaName,
        sqlDialect
    ) {
    override fun execute(sql: Sql?) {
        throw NotImplementedError("This JDBC Destination Handler does not support typing deduping")
    }

    override fun toDestinationState(json: JsonNode?): DestinationState {
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
