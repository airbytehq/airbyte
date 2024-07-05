/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.util.Optional
import org.jooq.DataType
import org.jooq.SQLDialect
import org.jooq.impl.DefaultDataType

class MysqlDestinationHandler(
    jdbcDatabase: JdbcDatabase,
    rawTableDatabaseName: String,
) :
    JdbcDestinationHandler<MinimumDestinationState>(
        // Mysql doesn't have an actual schema concept.
        // Instead, we put each namespace into its own database.
        null,
        jdbcDatabase,
        rawTableDatabaseName,
        SQLDialect.MYSQL,
    ) {
    override val stateTableUpdatedAtType: DataType<*> =
        DefaultDataType(SQLDialect.MYSQL, String::class.java, "datetime")
    override fun toJdbcTypeName(airbyteType: AirbyteType): String =
        // This is mostly identical to the postgres implementation, but swaps jsonb to json
        if (airbyteType is AirbyteProtocolType) {
            Companion.toJdbcTypeName(airbyteType)
        } else {
            when (airbyteType.typeName) {
                Struct.TYPE,
                UnsupportedOneOf.TYPE,
                Array.TYPE -> "json"
                Union.TYPE -> toJdbcTypeName((airbyteType as Union).chooseType())
                else -> throw IllegalArgumentException("Unsupported AirbyteType: $airbyteType")
            }
        }

    override fun isAirbyteRawIdColumnMatch(existingTable: TableDefinition): Boolean =
        // we create the raw_id column as a varchar rather than as text
        "VARCHAR" == existingTable.columns[JavaBaseConstants.COLUMN_NAME_AB_RAW_ID]!!.type

    override fun isAirbyteExtractedAtColumnMatch(existingTable: TableDefinition): Boolean =
        // the raw table uses a real timestamp column for backwards-compatibility reasons
        "TIMESTAMP" == existingTable.columns[JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT]!!.type

    override fun toDestinationState(json: JsonNode): MinimumDestinationState =
        MinimumDestinationState.Impl(
            json.hasNonNull("needsSoftReset") && json["needsSoftReset"].asBoolean(),
        )

    // Mysql doesn't have schemas. Pass the namespace as the database name.
    override fun findExistingTable(id: StreamId): Optional<TableDefinition> =
        findExistingTable(jdbcDatabase, id.finalNamespace, null, id.finalName)

    override fun getTableFromMetadata(dbmetadata: DatabaseMetaData, id: StreamId): ResultSet =
        dbmetadata.getTables(id.rawNamespace, null, id.rawName, null)

    companion object {
        private fun toJdbcTypeName(airbyteProtocolType: AirbyteProtocolType): String =
            when (airbyteProtocolType) {
                AirbyteProtocolType.STRING -> "text"
                AirbyteProtocolType.NUMBER -> "decimal"
                AirbyteProtocolType.INTEGER -> "bigint"
                AirbyteProtocolType.BOOLEAN -> "bit"
                AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> "varchar"
                AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> "datetime"
                AirbyteProtocolType.TIME_WITH_TIMEZONE -> "varchar"
                AirbyteProtocolType.TIME_WITHOUT_TIMEZONE -> "time"
                AirbyteProtocolType.DATE -> "date"
                AirbyteProtocolType.UNKNOWN -> "json"
            }
    }
}
