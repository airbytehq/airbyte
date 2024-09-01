/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.JavaBaseConstants.DestinationColumns
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil.getResultsOrLogAndThrowFirst
import io.airbyte.commons.concurrency.CompletableFutures
import io.airbyte.commons.exceptions.SQLRuntimeException
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.airbyte.integrations.base.destination.typing_deduping.*
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.*
import java.time.Instant
import java.time.OffsetDateTime
import java.time.temporal.ChronoUnit
import java.util.*
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionStage
import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.DataType
import org.jooq.SQLDialect
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.DSL.field
import org.jooq.impl.DSL.quotedName
import org.jooq.impl.DSL.table
import org.jooq.impl.SQLDataType

private val LOGGER = KotlinLogging.logger {}

abstract class JdbcDestinationHandler<DestinationState>(
    // JDBC's "catalog name" refers to e.g. the Postgres/Mysql database.
    // This is nullable because Mysql doesn't provide "schemas" within databses,
    // unlike Postgres.
    // For Postgres (and other systems supporting the database.schema.table
    // layers), set this to a nonnull value. We will create ALL tables in this
    // database.
    // For Mysql (and other systems with just a database.table layering),
    // set this to null and override the relevant methods to treat namespaces
    // as databases.
    protected val catalogName: String?,
    protected val jdbcDatabase: JdbcDatabase,
    protected val rawTableNamespace: String,
    private val dialect: SQLDialect,
    private val columns: DestinationColumns = DestinationColumns.V2_WITH_GENERATION,
    protected val generationHandler: JdbcGenerationHandler,
) : DestinationHandler<DestinationState> {
    protected val dslContext: DSLContext
        get() = DSL.using(dialect)

    protected open val stateTableUpdatedAtType: DataType<*> = SQLDataType.TIMESTAMPWITHTIMEZONE

    @Throws(Exception::class)
    protected open fun findExistingTable(id: StreamId): Optional<TableDefinition> {
        return findExistingTable(jdbcDatabase, catalogName, id.finalNamespace, id.finalName)
    }

    protected open fun getRawTableFromMetadata(
        dbmetadata: DatabaseMetaData,
        id: StreamId,
        suffix: String
    ): ResultSet = dbmetadata.getTables(catalogName, id.rawNamespace, id.rawName + suffix, null)

    @Throws(Exception::class)
    private fun isFinalTableEmpty(id: StreamId): Boolean {
        return !jdbcDatabase.queryBoolean(
            dslContext
                .select(
                    field(
                        DSL.exists(
                            DSL.selectOne().from(DSL.name(id.finalNamespace, id.finalName)).limit(1)
                        )
                    )
                )
                .getSQL(ParamType.INLINED)
        )
    }

    @Throws(Exception::class)
    private fun getInitialRawTableState(id: StreamId, suffix: String): InitialRawTableStatus {
        val tableExists =
            jdbcDatabase.executeMetadataQuery { dbmetadata: DatabaseMetaData ->
                LOGGER.info {
                    "Retrieving table from Db metadata: $catalogName ${id.rawNamespace} ${id.rawName}"
                }
                try {
                    getRawTableFromMetadata(dbmetadata, id, suffix).use { table ->
                        return@executeMetadataQuery table.next()
                    }
                } catch (e: SQLException) {
                    LOGGER.error(e) { "Failed to retrieve table info from metadata" }
                    throw SQLRuntimeException(e)
                }
            }
        if (!tableExists) {
            // There's no raw table at all. Therefore there are no unprocessed raw records, and this
            // sync
            // should not filter raw records by timestamp.
            return InitialRawTableStatus(false, false, Optional.empty())
        }

        jdbcDatabase
            .unsafeQuery(
                { conn: Connection ->
                    conn.prepareStatement(
                        dslContext
                            .select(field("MIN(_airbyte_extracted_at)").`as`("min_timestamp"))
                            .from(DSL.name(id.rawNamespace, id.rawName + suffix))
                            .where(DSL.condition("_airbyte_loaded_at IS NULL"))
                            .sql
                    )
                },
                { record: ResultSet -> record.getTimestamp("min_timestamp") }
            )
            .use { timestampStream ->
                // Filter for nonNull values in case the query returned NULL (i.e. no unloaded
                // records).
                val minUnloadedTimestamp: Optional<Timestamp> =
                    timestampStream.filter { obj: Timestamp? -> Objects.nonNull(obj) }.findFirst()
                if (minUnloadedTimestamp.isPresent) {
                    // Decrement by 1 second since timestamp precision varies between databases.
                    val ts =
                        minUnloadedTimestamp
                            .map { obj: Timestamp -> obj.toInstant() }
                            .map { i: Instant -> i.minus(1, ChronoUnit.SECONDS) }
                    return InitialRawTableStatus(true, true, ts)
                }
            }
        jdbcDatabase
            .unsafeQuery(
                { conn: Connection ->
                    conn.prepareStatement(
                        dslContext
                            .select(field("MAX(_airbyte_extracted_at)").`as`("min_timestamp"))
                            .from(DSL.name(id.rawNamespace, id.rawName + suffix))
                            .sql
                    )
                },
                { record: ResultSet -> record.getTimestamp("min_timestamp") }
            )
            .use { timestampStream ->
                // Filter for nonNull values in case the query returned NULL (i.e. no raw records at
                // all).
                val minUnloadedTimestamp: Optional<Timestamp> =
                    timestampStream.filter { obj: Timestamp? -> Objects.nonNull(obj) }.findFirst()
                return InitialRawTableStatus(
                    true,
                    false,
                    minUnloadedTimestamp.map { obj: Timestamp -> obj.toInstant() }
                )
            }
    }

    @Throws(Exception::class)
    override fun execute(sql: Sql) {
        val transactions: List<List<String>> = sql.transactions
        val queryId = UUID.randomUUID()
        for (transaction in transactions) {
            val transactionId = UUID.randomUUID()
            LOGGER.info {
                "Executing sql $queryId-$transactionId: ${transactions.joinToString("\n")}"
            }
            val startTime = System.currentTimeMillis()

            try {
                jdbcDatabase.executeWithinTransaction(transaction)
            } catch (e: SQLException) {
                LOGGER.error(e) { "Sql $queryId-$transactionId failed" }
                throw e
            }

            LOGGER.info {
                "Sql $queryId-$transactionId completed in ${System.currentTimeMillis() - startTime} ms"
            }
        }
    }

    @Throws(Exception::class)
    override fun gatherInitialState(
        streamConfigs: List<StreamConfig>
    ): List<DestinationInitialStatus<DestinationState>> {
        // Use stream n/ns pair because we don't want to build the full StreamId here
        val destinationStatesFuture =
            CompletableFuture.supplyAsync {
                try {
                    return@supplyAsync getAllDestinationStates()
                } catch (e: SQLException) {
                    throw RuntimeException(e)
                }
            }

        val initialStates =
            streamConfigs.map { streamConfig: StreamConfig ->
                retrieveState(destinationStatesFuture, streamConfig)
            }

        val states = CompletableFutures.allOf(initialStates).toCompletableFuture().join()
        return getResultsOrLogAndThrowFirst("Failed to retrieve initial state", states)
    }

    @Throws(SQLException::class)
    protected fun getAllDestinationStates(): Map<AirbyteStreamNameNamespacePair, DestinationState> {
        try {
            // Guarantee the table exists.
            jdbcDatabase.execute(
                dslContext
                    .createTableIfNotExists(
                        quotedName(rawTableNamespace, DESTINATION_STATE_TABLE_NAME),
                    )
                    .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME), SQLDataType.VARCHAR)
                    .column(
                        quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE),
                        SQLDataType.VARCHAR,
                    ) // Just use a string type, even if the destination has a json type.
                    // We're never going to query this column in a fancy way - all our processing
                    // can happen
                    // client-side.
                    .column(
                        quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE),
                        SQLDataType.VARCHAR,
                    ) // Add an updated_at field. We don't actually need it yet, but it can't hurt!
                    .column(
                        quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT),
                        stateTableUpdatedAtType,
                    )
                    .getSQL(ParamType.INLINED),
            )

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
                        .from(quotedName(rawTableNamespace, DESTINATION_STATE_TABLE_NAME))
                        .sql,
                )
                .map { recordJson: JsonNode ->
                    // Forcibly downcase all key names.
                    // This is to handle any destinations that upcase the column names.
                    // For example - Snowflake with QUOTED_IDENTIFIERS_IGNORE_CASE=TRUE.
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
                        OffsetDateTime.parse(updatedAt)
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
        } catch (e: Exception) {
            LOGGER.warn(e) { "Failed to retrieve destination states" }
            return emptyMap()
        }
    }

    private fun retrieveState(
        destinationStatesFuture:
            CompletableFuture<Map<AirbyteStreamNameNamespacePair, DestinationState>>,
        streamConfig: StreamConfig?
    ): CompletionStage<DestinationInitialStatus<DestinationState>> {
        return destinationStatesFuture.thenApply {
            destinationStates: Map<AirbyteStreamNameNamespacePair, DestinationState> ->
            try {
                val finalTableDefinition = findExistingTable(streamConfig!!.id)
                val isSchemaMismatch: Boolean
                val isFinalTableEmpty: Boolean
                if (finalTableDefinition.isPresent) {
                    isSchemaMismatch =
                        !existingSchemaMatchesStreamConfig(streamConfig, finalTableDefinition.get())
                    isFinalTableEmpty = isFinalTableEmpty(streamConfig.id)
                } else {
                    // If the final table doesn't exist, then by definition it doesn't have a schema
                    // mismatch and has no
                    // records.
                    isSchemaMismatch = false
                    isFinalTableEmpty = true
                }
                val initialRawTableState =
                    getInitialRawTableState(streamConfig.id, AbstractStreamOperation.NO_SUFFIX)
                val destinationState =
                    destinationStates.getOrDefault(
                        streamConfig.id.asPair(),
                        toDestinationState(Jsons.emptyObject())
                    )
                return@thenApply DestinationInitialStatus<DestinationState>(
                    streamConfig,
                    finalTableDefinition.isPresent,
                    initialRawTableState,
                    getInitialRawTableState(
                        streamConfig.id,
                        AbstractStreamOperation.TMP_TABLE_SUFFIX
                    ),
                    isSchemaMismatch,
                    isFinalTableEmpty,
                    destinationState,
                    finalTableGenerationId =
                        generationHandler.getGenerationIdInTable(
                            jdbcDatabase,
                            streamConfig.id.rawNamespace,
                            streamConfig.id.rawName
                        ),
                    finalTempTableGenerationId =
                        generationHandler.getGenerationIdInTable(
                            jdbcDatabase,
                            streamConfig.id.rawNamespace,
                            streamConfig.id.rawName + AbstractStreamOperation.TMP_TABLE_SUFFIX
                        ),
                )
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }
    }

    protected open fun isAirbyteRawIdColumnMatch(existingTable: TableDefinition): Boolean {
        return toJdbcTypeName(AirbyteProtocolType.STRING)
            .equals(
                existingTable.columns.getValue(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).type,
                ignoreCase = true,
            )
    }

    protected open fun isAirbyteExtractedAtColumnMatch(existingTable: TableDefinition): Boolean {
        return toJdbcTypeName(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE)
            .equals(
                existingTable.columns.getValue(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT).type,
                ignoreCase = true,
            )
    }

    protected open fun isAirbyteMetaColumnMatch(existingTable: TableDefinition): Boolean {
        return toJdbcTypeName(Struct(LinkedHashMap<String, AirbyteType>()))
            .equals(
                existingTable.columns.getValue(JavaBaseConstants.COLUMN_NAME_AB_META).type,
                ignoreCase = true,
            )
    }

    protected open fun isAirbyteGenerationColumnMatch(existingTable: TableDefinition): Boolean {
        return toJdbcTypeName(AirbyteProtocolType.INTEGER)
            .equals(
                existingTable.columns.getValue(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID).type,
                ignoreCase = true,
            )
    }

    open protected fun existingSchemaMatchesStreamConfig(
        stream: StreamConfig?,
        existingTable: TableDefinition
    ): Boolean {
        // Check that the columns match, with special handling for the metadata columns.
        if (
            !(existingTable.columns.containsKey(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID) &&
                isAirbyteRawIdColumnMatch(existingTable)) ||
                !(existingTable.columns.containsKey(
                    JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
                ) && isAirbyteExtractedAtColumnMatch(existingTable)) ||
                !(existingTable.columns.containsKey(JavaBaseConstants.COLUMN_NAME_AB_META) &&
                    isAirbyteMetaColumnMatch(existingTable)) ||
                (columns == DestinationColumns.V2_WITH_GENERATION &&
                    !(existingTable.columns.containsKey(
                        JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
                    ) && isAirbyteGenerationColumnMatch(existingTable)))
        ) {
            // Missing AB meta columns from final table, we need them to do proper T+D so trigger
            // soft-reset
            return false
        }
        val intendedColumns =
            LinkedHashMap(
                stream!!.columns.entries.associate { it.key.name to toJdbcTypeName(it.value) }
            )

        // Filter out Meta columns since they don't exist in stream config.
        val actualColumns = LinkedHashMap<String?, String>()
        existingTable.columns.entries
            .filter { column: Map.Entry<String?, ColumnDefinition> ->
                JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.none { it == column.key }
            }
            .forEach { actualColumns[it.key] = it.value.type.lowercase() }

        return actualColumns == intendedColumns
    }

    protected open fun getDeleteStatesSql(
        destinationStates: Map<StreamId, DestinationState>
    ): String {
        return dslContext
            .deleteFrom(table(quotedName(rawTableNamespace, DESTINATION_STATE_TABLE_NAME)))
            .where(
                destinationStates.keys
                    .map { streamId: StreamId ->
                        field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME))
                            .eq(streamId.originalName)
                            .and(
                                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE))
                                    .eq(streamId.originalNamespace)
                            )
                    }
                    .reduce { obj: Condition, arg2: Condition? -> obj.or(arg2) }
            )
            .getSQL(ParamType.INLINED)
    }

    @Throws(Exception::class)
    override fun commitDestinationStates(destinationStates: Map<StreamId, DestinationState>) {
        try {
            if (destinationStates.isEmpty()) {
                return
            }

            // Delete all state records where the stream name+namespace match one of our states
            var deleteStates = getDeleteStatesSql(destinationStates)

            // Reinsert all of our states
            var insertStatesStep =
                dslContext
                    .insertInto(table(quotedName(rawTableNamespace, DESTINATION_STATE_TABLE_NAME)))
                    .columns(
                        field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME), String::class.java),
                        field(
                            quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE),
                            String::class.java
                        ),
                        field(
                            quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE),
                            String::class.java
                        ), // This field is a timestamptz, but it's easier to just insert a string
                        // and assume the destination can cast it appropriately.
                        // Destination-specific timestamp syntax is weird and annoying.
                        field(
                            quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT),
                            String::class.java
                        )
                    )
            for ((streamId, value) in destinationStates) {
                val stateJson = Jsons.serialize(value)
                insertStatesStep =
                    insertStatesStep.values(
                        streamId.originalName,
                        streamId.originalNamespace,
                        stateJson,
                        OffsetDateTime.now().toString()
                    )
            }
            val insertStates = insertStatesStep.getSQL(ParamType.INLINED)

            executeWithinTransaction(listOf(deleteStates, insertStates))
        } catch (e: Exception) {
            LOGGER.warn(e) { "Failed to commit destination states" }
        }
    }

    @Throws(Exception::class)
    protected open fun executeWithinTransaction(statements: List<String>) {
        jdbcDatabase.executeWithinTransaction(statements)
    }

    /**
     * Convert to the TYPE_NAME retrieved from [java.sql.DatabaseMetaData.getColumns]
     *
     * @param airbyteType
     * @return
     */
    protected abstract fun toJdbcTypeName(airbyteType: AirbyteType): String

    protected abstract fun toDestinationState(json: JsonNode): DestinationState

    companion object {

        private const val DESTINATION_STATE_TABLE_NAME = "_airbyte_destination_state"
        private const val DESTINATION_STATE_TABLE_COLUMN_NAME = "name"
        private const val DESTINATION_STATE_TABLE_COLUMN_NAMESPACE = "namespace"
        private const val DESTINATION_STATE_TABLE_COLUMN_STATE = "destination_state"
        private const val DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT = "updated_at"

        @Throws(SQLException::class)
        fun findExistingTable(
            jdbcDatabase: JdbcDatabase,
            catalogName: String?,
            schemaName: String?,
            tableName: String?
        ): Optional<TableDefinition> {
            val retrievedColumnDefns =
                jdbcDatabase.executeMetadataQuery { dbMetadata: DatabaseMetaData ->

                    // TODO: normalize namespace and finalName strings to quoted-lowercase (as
                    // needed. Snowflake
                    // requires uppercase)
                    val columnDefinitions = LinkedHashMap<String, ColumnDefinition>()
                    LOGGER.info {
                        "Retrieving existing columns for $catalogName.$schemaName.$tableName"
                    }
                    try {
                        dbMetadata.getColumns(catalogName, schemaName, tableName, null).use {
                            columns ->
                            while (columns.next()) {
                                val columnName = columns.getString("COLUMN_NAME")
                                val typeName = columns.getString("TYPE_NAME")
                                val columnSize = columns.getInt("COLUMN_SIZE")
                                val isNullable = columns.getString("IS_NULLABLE")
                                columnDefinitions[columnName] =
                                    ColumnDefinition(
                                        columnName,
                                        typeName,
                                        columnSize,
                                        fromIsNullableIsoString(isNullable)
                                    )
                            }
                        }
                    } catch (e: SQLException) {
                        LOGGER.error(e) {
                            "Failed to retrieve column info for $catalogName.$schemaName.$tableName"
                        }
                        throw SQLRuntimeException(e)
                    }
                    columnDefinitions
                }
            // Guard to fail fast
            if (retrievedColumnDefns.isEmpty()) {
                return Optional.empty()
            }

            return Optional.of(TableDefinition(retrievedColumnDefns))
        }

        @JvmStatic
        fun fromIsNullableIsoString(isNullable: String?): Boolean {
            return "YES".equals(isNullable, ignoreCase = true)
        }
    }
}
