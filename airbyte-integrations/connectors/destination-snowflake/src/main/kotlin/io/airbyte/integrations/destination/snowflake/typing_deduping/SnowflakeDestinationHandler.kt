/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabaseUtils.toSqlTypeName
import io.airbyte.integrations.destination.snowflake.migrations.SnowflakeState
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.SQLException
import java.time.Instant
import java.util.*
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.apache.commons.text.StringSubstitutor
import org.jooq.SQLDialect
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class SnowflakeDestinationHandler(
    databaseName: String,
    private val database: JdbcDatabase,
    rawTableSchema: String
) :
    JdbcDestinationHandler<SnowflakeState>(
        databaseName,
        database,
        rawTableSchema,
        SQLDialect.POSTGRES
    ) {
    // Postgres is close enough to Snowflake SQL for our purposes.
    // We don't quote the database name in any queries, so just upcase it.
    private val databaseName = databaseName.uppercase(Locale.getDefault())

    @Throws(SQLException::class)
    private fun getFinalTableRowCount(
        streamIds: List<StreamId>
    ): LinkedHashMap<String, LinkedHashMap<String, Int>> {
        val tableRowCounts = LinkedHashMap<String, LinkedHashMap<String, Int>>()
        // convert list stream to array
        val namespaces = streamIds.map { it.finalNamespace }.toTypedArray()
        val names = streamIds.map { it.finalName }.toTypedArray()
        val query =
            """
                         SELECT table_schema, table_name, row_count
                         FROM information_schema.tables
                         WHERE table_catalog = ?
                           AND table_schema IN (${IntRange(1, streamIds.size).joinToString { "?" }})
                           AND table_name IN (${IntRange(1, streamIds.size).joinToString { "?" }})
                         
                         """.trimIndent()
        val bindValues = arrayOfNulls<String>(streamIds.size * 2 + 1)
        bindValues[0] = databaseName
        System.arraycopy(namespaces, 0, bindValues, 1, namespaces.size)
        System.arraycopy(names, 0, bindValues, namespaces.size + 1, names.size)
        val results = database.queryJsons(query, *bindValues)
        for (result in results) {
            val tableSchema = result["TABLE_SCHEMA"].asText()
            val tableName = result["TABLE_NAME"].asText()
            val rowCount = result["ROW_COUNT"].asInt()
            tableRowCounts.computeIfAbsent(tableSchema) { LinkedHashMap() }[tableName] = rowCount
        }
        return tableRowCounts
    }

    @Throws(Exception::class)
    private fun getInitialRawTableState(
        id: StreamId,
        destinationSyncMode: DestinationSyncMode
    ): InitialRawTableStatus {
        // Short-circuit for overwrite, table will be truncated anyway
        if (destinationSyncMode == DestinationSyncMode.OVERWRITE) {
            return InitialRawTableStatus(false, false, Optional.empty())
        }
        val tableExists =
            database.executeMetadataQuery { databaseMetaData: DatabaseMetaData? ->
                LOGGER.info("Retrieving table from Db metadata: {} {}", id.rawNamespace, id.rawName)
                try {
                    databaseMetaData!!
                        .getTables(databaseName, id.rawNamespace, id.rawName, null)
                        .use { tables ->
                            return@executeMetadataQuery tables.next()
                        }
                } catch (e: SQLException) {
                    LOGGER.error("Failed to retrieve table metadata", e)
                    throw RuntimeException(e)
                }
            }
        if (!tableExists) {
            return InitialRawTableStatus(false, false, Optional.empty())
        }
        // Snowflake timestamps have nanosecond precision, so decrement by 1ns
        // And use two explicit queries because COALESCE doesn't short-circuit.
        // This first query tries to find the oldest raw record with loaded_at = NULL
        val minUnloadedTimestamp =
            Optional.ofNullable(
                database
                    .queryStrings(
                        { conn: Connection ->
                            conn
                                .createStatement()
                                .executeQuery(
                                    StringSubstitutor(
                                            java.util.Map.of(
                                                "raw_table",
                                                id.rawTableId(SnowflakeSqlGenerator.QUOTE)
                                            )
                                        )
                                        .replace(
                                            """
                WITH MIN_TS AS (
                  SELECT TIMESTAMPADD(NANOSECOND, -1,
                    MIN(TIMESTAMPADD(
                      HOUR,
                      EXTRACT(timezone_hour from "_airbyte_extracted_at"),
                        TIMESTAMPADD(
                          MINUTE,
                          EXTRACT(timezone_minute from "_airbyte_extracted_at"),
                          CONVERT_TIMEZONE('UTC', "_airbyte_extracted_at")
                        )
                    ))) AS MIN_TIMESTAMP
                  FROM ${'$'}{raw_table}
                  WHERE "_airbyte_loaded_at" IS NULL
                ) SELECT TO_VARCHAR(MIN_TIMESTAMP,'YYYY-MM-DDTHH24:MI:SS.FF9TZH:TZM') as MIN_TIMESTAMP_UTC from MIN_TS;
                
                """.trimIndent()
                                        )
                                )
                        }, // The query will always return exactly one record, so use .get(0)
                        { record: ResultSet -> record.getString("MIN_TIMESTAMP_UTC") }
                    )
                    .first()
            )
        if (minUnloadedTimestamp.isPresent) {
            return InitialRawTableStatus(
                true,
                true,
                minUnloadedTimestamp.map { text: String? -> Instant.parse(text) }
            )
        }

        // If there are no unloaded raw records, then we can safely skip all existing raw records.
        // This second query just finds the newest raw record.

        // This is _technically_ wrong, because during the DST transition we might select
        // the wrong max timestamp. We _should_ do the UTC conversion inside the CTE, but that's a
        // lot
        // of work for a very small edge case.
        // We released the fix to write extracted_at in UTC before DST changed, so this is fine.
        val maxTimestamp =
            Optional.ofNullable(
                database
                    .queryStrings(
                        { conn: Connection ->
                            conn
                                .createStatement()
                                .executeQuery(
                                    StringSubstitutor(
                                            java.util.Map.of(
                                                "raw_table",
                                                id.rawTableId(SnowflakeSqlGenerator.QUOTE)
                                            )
                                        )
                                        .replace(
                                            """
                WITH MAX_TS AS (
                  SELECT MAX("_airbyte_extracted_at")
                  AS MAX_TIMESTAMP
                  FROM ${'$'}{raw_table}
                ) SELECT TO_VARCHAR(
                  TIMESTAMPADD(
                    HOUR,
                    EXTRACT(timezone_hour from MAX_TIMESTAMP),
                    TIMESTAMPADD(
                      MINUTE,
                      EXTRACT(timezone_minute from MAX_TIMESTAMP),
                      CONVERT_TIMEZONE('UTC', MAX_TIMESTAMP)
                    )
                ),'YYYY-MM-DDTHH24:MI:SS.FF9TZH:TZM') as MAX_TIMESTAMP_UTC from MAX_TS;
                
                """.trimIndent()
                                        )
                                )
                        },
                        { record: ResultSet -> record.getString("MAX_TIMESTAMP_UTC") }
                    )
                    .first()
            )
        return InitialRawTableStatus(
            true,
            false,
            maxTimestamp.map { text: String? -> Instant.parse(text) }
        )
    }

    @Throws(Exception::class)
    override fun execute(sql: Sql) {
        val transactions = sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT")
        val queryId = UUID.randomUUID()
        for (transaction in transactions) {
            val transactionId = UUID.randomUUID()
            LOGGER.info("Executing sql {}-{}: {}", queryId, transactionId, transaction)
            val startTime = System.currentTimeMillis()

            try {
                database.execute(transaction)
            } catch (e: SnowflakeSQLException) {
                LOGGER.error("Sql {} failed", queryId, e)
                // Snowflake SQL exceptions by default may not be super helpful, so we try to
                // extract the relevant
                // part of the message.
                val trimmedMessage =
                    if (e.message!!.startsWith(EXCEPTION_COMMON_PREFIX)) {
                        // The first line is a pretty generic message, so just remove it
                        e.message!!.substring(e.message!!.indexOf("\n") + 1)
                    } else {
                        e.message
                    }
                throw RuntimeException(trimmedMessage, e)
            }

            LOGGER.info(
                "Sql {}-{} completed in {} ms",
                queryId,
                transactionId,
                System.currentTimeMillis() - startTime
            )
        }
    }

    private fun getPks(stream: StreamConfig?): Set<String> {
        return if (stream?.primaryKey != null) stream.primaryKey.map { it.name }.toSet()
        else emptySet()
    }

    override fun isAirbyteRawIdColumnMatch(existingTable: TableDefinition): Boolean {
        val abRawIdColumnName: String =
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID.uppercase(Locale.getDefault())
        return existingTable.columns.containsKey(abRawIdColumnName) &&
            toJdbcTypeName(AirbyteProtocolType.STRING) ==
                existingTable.columns[abRawIdColumnName]!!.type
    }

    override fun isAirbyteExtractedAtColumnMatch(existingTable: TableDefinition): Boolean {
        val abExtractedAtColumnName: String =
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT.uppercase(Locale.getDefault())
        return existingTable.columns.containsKey(abExtractedAtColumnName) &&
            toJdbcTypeName(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE) ==
                existingTable.columns[abExtractedAtColumnName]!!.type
    }

    override fun isAirbyteMetaColumnMatch(existingTable: TableDefinition): Boolean {
        val abMetaColumnName: String =
            JavaBaseConstants.COLUMN_NAME_AB_META.uppercase(Locale.getDefault())
        return existingTable.columns.containsKey(abMetaColumnName) &&
            "VARIANT" == existingTable.columns[abMetaColumnName]!!.type
    }

    override fun existingSchemaMatchesStreamConfig(
        stream: StreamConfig?,
        existingTable: TableDefinition
    ): Boolean {
        val pks = getPks(stream)
        // This is same as JdbcDestinationHandler#existingSchemaMatchesStreamConfig with upper case
        // conversion.
        // TODO: Unify this using name transformer or something.
        if (
            !isAirbyteRawIdColumnMatch(existingTable) ||
                !isAirbyteExtractedAtColumnMatch(existingTable) ||
                !isAirbyteMetaColumnMatch(existingTable)
        ) {
            // Missing AB meta columns from final table, we need them to do proper T+D so trigger
            // soft-reset
            return false
        }
        // Rewritten in Kotlin
        // https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-snowflake/src/main/java/io/airbyte/integrations/destination/snowflake/typing_deduping/SnowflakeDestinationHandler.java#L270-L287
        val intendedColumns: LinkedHashMap<String, String> =
            stream!!.columns.asSequence().associateTo(LinkedHashMap()) {
                it.key.name to toJdbcTypeName(it.value)
            }
        // Filter out Meta columns since they don't exist in stream config.
        val actualColumns: LinkedHashMap<String, String> =
            existingTable.columns
                .filter { it ->
                    V2_FINAL_TABLE_METADATA_COLUMNS.map { it.uppercase() }
                        .none { abCol -> abCol == it.key }
                }
                .asSequence()
                .associateTo(LinkedHashMap()) { it.key!! to it.value.type }
        // soft-resetting https://github.com/airbytehq/airbyte/pull/31082
        val hasPksWithNonNullConstraint: Boolean =
            existingTable.columns.any { pks.contains(it.key) && !it.value.isNullable }

        return !hasPksWithNonNullConstraint && actualColumns == intendedColumns
    }

    @Throws(Exception::class)
    override fun gatherInitialState(
        streamConfigs: List<StreamConfig>
    ): List<DestinationInitialStatus<SnowflakeState>> {
        val destinationStates: Map<AirbyteStreamNameNamespacePair, SnowflakeState> =
            super.getAllDestinationStates()

        val streamIds = streamConfigs.map { it.id }.toList()
        val existingTables = findExistingTables(database, databaseName, streamIds)
        val tableRowCounts = getFinalTableRowCount(streamIds)
        return streamConfigs
            .stream()
            .map { streamConfig: StreamConfig ->
                try {
                    val namespace = streamConfig.id.finalNamespace.uppercase(Locale.getDefault())
                    val name = streamConfig.id.finalName.uppercase(Locale.getDefault())
                    var isSchemaMismatch = false
                    var isFinalTableEmpty = true
                    val isFinalTablePresent =
                        existingTables.containsKey(namespace) &&
                            existingTables[namespace]!!.containsKey(name)
                    val hasRowCount =
                        tableRowCounts.containsKey(namespace) &&
                            tableRowCounts[namespace]!!.containsKey(name)
                    if (isFinalTablePresent) {
                        val existingTable = existingTables[namespace]!![name]
                        isSchemaMismatch =
                            !existingSchemaMatchesStreamConfig(streamConfig, existingTable!!)
                        isFinalTableEmpty = hasRowCount && tableRowCounts[namespace]!![name] == 0
                    }
                    val initialRawTableState =
                        getInitialRawTableState(streamConfig.id, streamConfig.destinationSyncMode)
                    val destinationState: SnowflakeState =
                        destinationStates.getOrDefault(
                            streamConfig.id.asPair(),
                            toDestinationState(emptyObject())
                        )
                    return@map DestinationInitialStatus<SnowflakeState>(
                        streamConfig,
                        isFinalTablePresent,
                        initialRawTableState,
                        isSchemaMismatch,
                        isFinalTableEmpty,
                        destinationState
                    )
                } catch (e: Exception) {
                    throw RuntimeException(e)
                }
            }
            .toList()
    }

    override fun toJdbcTypeName(airbyteType: AirbyteType): String {
        if (airbyteType is AirbyteProtocolType) {
            return toJdbcTypeName(airbyteType)
        }

        return when (airbyteType.typeName) {
            Struct.TYPE -> "OBJECT"
            Array.TYPE -> "ARRAY"
            UnsupportedOneOf.TYPE -> "VARIANT"
            Union.TYPE -> toJdbcTypeName((airbyteType as Union).chooseType())
            else -> throw IllegalArgumentException("Unrecognized type: " + airbyteType.typeName)
        }
    }

    override fun toDestinationState(json: JsonNode): SnowflakeState {
        return SnowflakeState(
            json.hasNonNull("needsSoftReset") && json["needsSoftReset"].asBoolean()
        )
    }

    private fun toJdbcTypeName(airbyteProtocolType: AirbyteProtocolType): String {
        return toSqlTypeName(airbyteProtocolType)
    }

    override fun createNamespaces(schemas: Set<String>) {
        // do nothing?
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(SnowflakeDestinationHandler::class.java)
        const val EXCEPTION_COMMON_PREFIX: String =
            "JavaScript execution error: Uncaught Execution of multiple statements failed on statement"

        @JvmStatic
        @Throws(SQLException::class)
        fun findExistingTables(
            database: JdbcDatabase,
            databaseName: String,
            streamIds: List<StreamId>
        ): LinkedHashMap<String, LinkedHashMap<String, TableDefinition>> {
            val existingTables = LinkedHashMap<String, LinkedHashMap<String, TableDefinition>>()
            // convert list stream to array
            val namespaces = streamIds.map { it.finalNamespace }.toTypedArray()
            val names = streamIds.map { it.finalName }.toTypedArray()
            val query =
                """
                         SELECT table_schema, table_name, column_name, data_type, is_nullable
                         FROM information_schema.columns
                         WHERE table_catalog = ?
                           AND table_schema IN (${IntRange(1, streamIds.size).joinToString { "?" }})
                           AND table_name IN (${IntRange(1, streamIds.size).joinToString { "?" }})
                         ORDER BY table_schema, table_name, ordinal_position;
                         """.trimIndent()
            val bindValues = arrayOfNulls<String>(streamIds.size * 2 + 1)
            bindValues[0] = databaseName.uppercase(Locale.getDefault())
            System.arraycopy(namespaces, 0, bindValues, 1, namespaces.size)
            System.arraycopy(names, 0, bindValues, namespaces.size + 1, names.size)
            val results = database.queryJsons(query, *bindValues)
            for (result in results) {
                val tableSchema = result["TABLE_SCHEMA"].asText()
                val tableName = result["TABLE_NAME"].asText()
                val columnName = result["COLUMN_NAME"].asText()
                val dataType = result["DATA_TYPE"].asText()
                val isNullable = result["IS_NULLABLE"].asText()
                val tableDefinition =
                    existingTables
                        .computeIfAbsent(tableSchema) { _: String? -> LinkedHashMap() }
                        .computeIfAbsent(tableName) { _: String? ->
                            TableDefinition(LinkedHashMap())
                        }
                tableDefinition.columns[columnName] =
                    ColumnDefinition(columnName, dataType, 0, fromIsNullableIsoString(isNullable))
            }
            return existingTables
        }
    }
}
