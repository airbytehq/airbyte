/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import org.jooq.SQLDialect

class PostgresDestinationHandler(
    databaseName: String?,
    jdbcDatabase: JdbcDatabase,
    rawTableSchema: String
) :
    JdbcDestinationHandler<PostgresState>(
        databaseName,
        jdbcDatabase,
        rawTableSchema,
        SQLDialect.POSTGRES
    ) {
    override fun toJdbcTypeName(airbyteType: AirbyteType): String {
        // This is mostly identical to the postgres implementation, but swaps jsonb to super
        if (airbyteType is AirbyteProtocolType) {
            return toJdbcTypeName(airbyteType)
        }
        return when (airbyteType.typeName) {
            Struct.TYPE,
            UnsupportedOneOf.TYPE,
            Array.TYPE -> "jsonb"
            Union.TYPE -> toJdbcTypeName((airbyteType as Union).chooseType())
            else -> throw IllegalArgumentException("Unsupported AirbyteType: $airbyteType")
        }
    }

    override fun toDestinationState(json: JsonNode): PostgresState {
        return PostgresState(
            json.hasNonNull("needsSoftReset") && json["needsSoftReset"].asBoolean(),
            json.hasNonNull("isAirbyteMetaPresentInRaw") &&
                json["isAirbyteMetaPresentInRaw"].asBoolean()
        )
    }

    override fun createNamespaces(schemas: Set<String>) {
        TODO("Not yet implemented")
    }

    private fun toJdbcTypeName(airbyteProtocolType: AirbyteProtocolType): String {
        return when (airbyteProtocolType) {
            AirbyteProtocolType.STRING -> "varchar"
            AirbyteProtocolType.NUMBER -> "numeric"
            AirbyteProtocolType.INTEGER -> "int8"
            AirbyteProtocolType.BOOLEAN -> "bool"
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> "timestamptz"
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp"
            AirbyteProtocolType.TIME_WITH_TIMEZONE -> "timetz"
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE -> "time"
            AirbyteProtocolType.DATE -> "date"
            AirbyteProtocolType.UNKNOWN -> "jsonb"
        }
    }
}
