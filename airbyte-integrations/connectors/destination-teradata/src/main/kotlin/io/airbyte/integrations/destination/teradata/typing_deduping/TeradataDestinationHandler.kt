/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.teradata.TeradataSqlOperations.Companion
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.*
import org.jooq.Condition
import org.jooq.SQLDialect
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.DSL.field
import org.jooq.impl.DSL.quotedName
import org.jooq.impl.DSL.table
import org.jooq.impl.SQLDataType
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * A handler for destination-specific operations for Teradata. This class provides implementations
 * for managing destination states, mapping Airbyte types to JDBC types, and interacting with the
 * Teradata destination.
 *
 * @param jdbcDatabase The JDBC database instance used to interact with the database.
 * @param rawTableSchema The schema for the raw table in the database.
 * @param generationHandler The handler for generating the SQL for database operations.
 */
class TeradataDestinationHandler(
    jdbcDatabase: JdbcDatabase,
    rawTableSchema: String,
    generationHandler: JdbcGenerationHandler,
) :
    JdbcDestinationHandler<MinimumDestinationState>(
        null,
        jdbcDatabase,
        rawTableSchema,
        SQLDialect.DEFAULT,
        generationHandler = generationHandler
    ) {
    /**
     * Converts a JSON node into a `MinimumDestinationState` object.
     *
     * @param json The JSON node representing the destination state.
     * @return A `MinimumDestinationState` object.
     */
    override fun toDestinationState(json: JsonNode): MinimumDestinationState =
        MinimumDestinationState.Impl(
            json.hasNonNull("needsSoftReset") && json["needsSoftReset"].asBoolean(),
        )

    override fun createNamespaces(schemas: Set<String>) {
        TODO("Not yet implemented")
    }
    /**
     * Converts an Airbyte type to its corresponding JDBC type name.
     *
     * @param airbyteType The Airbyte type to convert.
     * @return The JDBC type name.
     * @throws IllegalArgumentException If the Airbyte type is unsupported.
     */
    override fun toJdbcTypeName(airbyteType: AirbyteType): String {
        val type =
            if (airbyteType is AirbyteProtocolType) {
                Companion.toJdbcTypeName(airbyteType)
            } else {
                when (airbyteType.typeName) {
                    Struct.TYPE,
                    Array.TYPE -> "json"
                    else -> throw IllegalArgumentException("Unsupported AirbyteType: $airbyteType")
                }
            }
        return type
    }
    /**
     * Checks if the final table is empty for the given stream ID.
     *
     * @param id The stream ID to check.
     * @return `true` if the table is empty, `false` otherwise.
     * @throws SQLException If there is an error during the query execution.
     */
    @Throws(Exception::class)
    override fun isFinalTableEmpty(id: StreamId): Boolean {
        try {
            return !jdbcDatabase.queryBoolean(
                dslContext
                    .select(
                        DSL.case_()
                            .`when`<Int>(
                                field<Int>(
                                        DSL.select<Int>(DSL.count())
                                            .from(DSL.name(id.finalNamespace, id.finalName)),
                                    )
                                    .gt(0),
                                DSL.inline(1),
                            )
                            .otherwise(DSL.inline(0))
                            .`as`("exists_flag"),
                    )
                    .getSQL(ParamType.INLINED),
            )
        } catch (se: SQLException) {
            if (se.errorCode == 3807) {
                LOGGER.warn(
                    "Table $id.finalNamespace.$id.finalNamespace does not exists.",
                )
            }
            throw se
        }
    }
    /**
     * Generates an SQL query to delete destination states from the destination state table.
     *
     * @param destinationStates A map of stream IDs to their corresponding destination states.
     * @return The SQL query for deleting destination states.
     */
    override fun getDeleteStatesSql(
        destinationStates: Map<StreamId, MinimumDestinationState>
    ): String {
        val query =
            dslContext
                .deleteFrom(
                    table(
                        quotedName(
                            rawTableNamespace,
                            DESTINATION_STATE_TABLE_NAME,
                        ),
                    ),
                )
                .where(
                    destinationStates.keys
                        .stream()
                        .map { streamId: StreamId ->
                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME))
                                .eq(streamId.originalName)
                                .and(
                                    field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE))
                                        .eq(streamId.originalNamespace),
                                )
                        }
                        .reduce(DSL.noCondition()) { obj: Condition, arg2: Condition? ->
                            obj.or(arg2)
                        },
                )
                .getSQL(ParamType.INLINED)
        return query
    }
    /**
     * Commits the given destination states to the database.
     *
     * @param destinationStates A map of stream IDs to their corresponding destination states.
     */
    override fun commitDestinationStates(
        destinationStates: Map<StreamId, MinimumDestinationState>
    ) {
        try {
            if (destinationStates.isEmpty()) {
                return
            }

            // Delete all state records where the stream name+namespace match one of our states
            val sqlStatementsDestinationState: MutableList<String> = ArrayList()
            sqlStatementsDestinationState.add(getDeleteStatesSql(destinationStates))

            for ((streamId, value) in destinationStates) {
                val stateJson = Jsons.serialize(value)

                val currentTime =
                    Timestamp.from(
                        Instant.ofEpochMilli(System.currentTimeMillis())
                            .atZone(ZoneOffset.UTC)
                            .toInstant(),
                    )

                // Reinsert all of our states
                val insertStatesStep: String =
                    dslContext
                        .insertInto(
                            table(
                                quotedName(
                                    rawTableNamespace,
                                    DESTINATION_STATE_TABLE_NAME,
                                ),
                            ),
                        )
                        .columns(
                            field(
                                quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME),
                                String::class.java
                            ),
                            field(
                                quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE),
                                String::class.java,
                            ),
                            field(
                                quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE),
                                String::class.java
                            ),
                            field(
                                quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT),
                                Timestamp::class.java
                            ),
                        )
                        .values(
                            streamId.originalName,
                            streamId.originalNamespace,
                            stateJson,
                            currentTime,
                        )
                        .getSQL(ParamType.INLINED)
                sqlStatementsDestinationState.add(insertStatesStep)
            }

            executeWithinTransaction(sqlStatementsDestinationState)
        } catch (e: java.lang.Exception) {
            LOGGER.warn("Failed to commit destination states", e)
        }
    }

    private fun isTableExists(schemaName: String?, tableName: String?): Boolean {
        val countQuery =
            dslContext
                .select(DSL.count())
                .from(DSL.table("DBC.TablesV"))
                .where(
                    DSL.field("TableName")
                        .eq(tableName)
                        .and(DSL.field("DataBaseName").eq(schemaName))
                )
                .getSQL(ParamType.INLINED)

        return jdbcDatabase.queryInt(countQuery) >
            0 // If the result is greater than 0, return true, else false
    }

    /**
     * Retrieves all destination states from the database.
     *
     * @return A map of stream names and namespaces to their corresponding destination states.
     */
    override fun getAllDestinationStates():
        Map<AirbyteStreamNameNamespacePair, MinimumDestinationState> {
        try {
            if (!isTableExists(rawTableNamespace, DESTINATION_STATE_TABLE_NAME)) {
                val sqlStatement: String =
                    dslContext
                        .createTable(quotedName(rawTableNamespace, DESTINATION_STATE_TABLE_NAME))
                        .column(
                            quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME),
                            SQLDataType.VARCHAR(256)
                        )
                        .column(
                            quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE),
                            SQLDataType.VARCHAR(256),
                        )
                        .column(
                            quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE),
                            SQLDataType.VARCHAR(256)
                        )
                        .column(
                            quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT),
                            stateTableUpdatedAtType,
                        )
                        .getSQL(ParamType.INLINED)
                jdbcDatabase.execute(sqlStatement)
            }

            // Fetch all records from it. We _could_ filter down to just our streams... but meh.
            // This is small
            // data.
            return jdbcDatabase
                .queryJsons(
                    dslContext
                        .select(
                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME)),
                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE)),
                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE)),
                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT)),
                        )
                        .from(
                            quotedName(
                                rawTableNamespace,
                                DESTINATION_STATE_TABLE_NAME,
                            ),
                        )
                        .sql,
                )
                .map { recordJson: JsonNode ->
                    val record = recordJson as ObjectNode
                    val newFields: HashMap<String, JsonNode> = HashMap()

                    val it = record.fieldNames()
                    while (it.hasNext()) {
                        val fieldName = it.next()
                        // We can't directly call record.set here, because that will raise a
                        // ConcurrentModificationException on the fieldnames iterator.
                        // Instead, build up a map of new fields and set them all at once.
                        newFields[fieldName.lowercase(Locale.getDefault())] = record[fieldName]
                    }
                    record.setAll<JsonNode>(newFields)

                    record
                }
                .sortedBy {
                    // Sort by updated_at, so that if there are duplicate state,
                    // the most recent state is the one that gets used.
                    // That shouldn't typically happen, but let's be defensive.
                    val updatedAt = it.get(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT)?.asText()
                    if (updatedAt != null) {
                        LocalDateTime.parse(updatedAt).atOffset(ZoneOffset.UTC)
                    } else {
                        OffsetDateTime.MIN
                    }
                }
                .associate {
                    val stateTextNode: JsonNode? = it.get(DESTINATION_STATE_TABLE_COLUMN_STATE)
                    val stateNode =
                        if (stateTextNode != null) Jsons.deserialize(stateTextNode.asText())
                        else Jsons.emptyObject()
                    val airbyteStreamNameNamespacePair =
                        AirbyteStreamNameNamespacePair(
                            it.get(DESTINATION_STATE_TABLE_COLUMN_NAME)?.asText(),
                            it.get(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE)?.asText(),
                        )

                    airbyteStreamNameNamespacePair to toDestinationState(stateNode)
                }
        } catch (e: java.lang.Exception) {
            LOGGER.warn("Failed to retrieve destination states", e)
            return emptyMap()
        }
    }
    /**
     * Finds the existing table for the given stream ID.
     *
     * @param id The stream ID.
     * @return An optional `TableDefinition` object representing the existing table, if found.
     */
    override fun findExistingTable(id: StreamId): Optional<TableDefinition> =
        if (isTableExists(id.finalNamespace, id.finalName)) {
            findExistingTable(jdbcDatabase, id.finalNamespace, null, id.finalName)
        } else {
            Optional.empty()
        }
    /**
     * Executes a list of SQL statements within a transaction.
     *
     * @param sql The SQL statements to execute.
     */
    override fun execute(sql: Sql) {
        val transactions: List<List<String>> = sql.transactions
        for (transaction in transactions) {
            try {
                jdbcDatabase.executeWithinTransaction(transaction)
            } catch (se: SQLException) {
                // Ignoring specific error codes i.e. object already exists, object does not exist
                if (se.errorCode !in ignorableErrorCodes) {
                    throw se
                }
            }
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(TeradataDestinationHandler::class.java)
        private const val DESTINATION_STATE_TABLE_COLUMN_STATE: String = "destination_state"
        private const val DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT: String = "updated_at"
        private const val DESTINATION_STATE_TABLE_NAME = "_airbyte_destination_state"
        private const val DESTINATION_STATE_TABLE_COLUMN_NAME = "name"
        private const val DESTINATION_STATE_TABLE_COLUMN_NAMESPACE = "namespace"
        // Define a set of error codes that should be ignored
        private val ignorableErrorCodes = setOf(5612, 3807, 3598, 3803)
        /**
         * Converts an Airbyte Protocol type to a JDBC type name.
         *
         * @param airbyteProtocolType The Airbyte Protocol type.
         * @return The corresponding JDBC type name.
         */
        private fun toJdbcTypeName(airbyteProtocolType: AirbyteProtocolType): String {
            val test =
                when (airbyteProtocolType) {
                    AirbyteProtocolType.STRING -> "varchar"
                    AirbyteProtocolType.NUMBER -> "float"
                    AirbyteProtocolType.INTEGER -> "bigint"
                    AirbyteProtocolType.BOOLEAN -> "smallint"
                    AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> "timestamp with time zone"
                    AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp"
                    AirbyteProtocolType.TIME_WITH_TIMEZONE -> "time with time zone"
                    AirbyteProtocolType.TIME_WITHOUT_TIMEZONE -> "time"
                    AirbyteProtocolType.DATE -> "date"
                    AirbyteProtocolType.UNKNOWN -> "json"
                }
            return test
        }
    }
}
