/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.of
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.transactionally
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.sql.Timestamp
import java.time.Instant
import java.util.Locale
import java.util.Optional
import java.util.stream.Collectors
import kotlin.Int
import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.DataType
import org.jooq.Field
import org.jooq.InsertValuesStepN
import org.jooq.Name
import org.jooq.Record
import org.jooq.SQLDialect
import org.jooq.SelectConditionStep
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType

abstract class JdbcSqlGenerator
@JvmOverloads
constructor(
    protected val namingTransformer: NamingConventionTransformer,
    private val cascadeDrop: Boolean = false
) : SqlGenerator {
    protected val cdcDeletedAtColumn: ColumnId = buildColumnId("_ab_cdc_deleted_at")

    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        return StreamId(
            namingTransformer.getNamespace(namespace),
            namingTransformer.convertStreamName(name),
            namingTransformer.getNamespace(rawNamespaceOverride),
            namingTransformer.convertStreamName(concatenateRawTableName(namespace, name)),
            namespace,
            name,
        )
    }

    override fun buildColumnId(name: String, suffix: String?): ColumnId {
        val nameWithSuffix = name + suffix
        return ColumnId(
            namingTransformer.getIdentifier(nameWithSuffix),
            name,
            namingTransformer.getIdentifier(nameWithSuffix),
        )
    }

    protected fun toDialectType(type: AirbyteType): DataType<*> {
        if (type is AirbyteProtocolType) {
            return toDialectType(type)
        }
        return when (type.typeName) {
            Struct.TYPE,
            UnsupportedOneOf.TYPE -> structType
            Array.TYPE -> arrayType
            Union.TYPE -> toDialectType((type as Union).chooseType())
            else -> throw IllegalArgumentException("Unsupported AirbyteType: $type")
        }
    }

    @VisibleForTesting
    open fun toDialectType(airbyteProtocolType: AirbyteProtocolType): DataType<*> {
        return when (airbyteProtocolType) {
            AirbyteProtocolType.STRING -> SQLDataType.VARCHAR(65535)
            AirbyteProtocolType.NUMBER -> SQLDataType.DECIMAL(38, 9)
            AirbyteProtocolType.INTEGER -> SQLDataType.BIGINT
            AirbyteProtocolType.BOOLEAN -> SQLDataType.BOOLEAN
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> SQLDataType.TIMESTAMPWITHTIMEZONE
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> SQLDataType.TIMESTAMP
            AirbyteProtocolType.TIME_WITH_TIMEZONE -> SQLDataType.TIMEWITHTIMEZONE
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE -> SQLDataType.TIME
            AirbyteProtocolType.DATE -> SQLDataType.DATE
            AirbyteProtocolType.UNKNOWN -> widestType
        }
    }

    protected abstract val structType: DataType<*>

    protected abstract val arrayType: DataType<*>

    @get:VisibleForTesting
    val timestampWithTimeZoneType: DataType<*>
        get() = toDialectType(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE)

    protected abstract val widestType: DataType<*>

    protected abstract val dialect: SQLDialect

    /**
     * @param columns from the schema to be extracted from _airbyte_data column. Use the destination
     * specific syntax to extract data
     * @param useExpensiveSaferCasting
     * @return a list of jooq fields for the final table insert statement.
     */
    protected abstract fun extractRawDataFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        useExpensiveSaferCasting: Boolean
    ): MutableList<Field<*>>

    /**
     *
     * @param columns from the schema to be used for type casting errors and construct _airbyte_meta
     * column
     * @return
     */
    protected abstract fun buildAirbyteMetaColumn(
        columns: LinkedHashMap<ColumnId, AirbyteType>
    ): Field<*>

    /**
     * Get the cdc_deleted_at column condition for append_dedup mode by extracting it from
     * _airbyte_data column in raw table.
     *
     * @return
     */
    protected abstract fun cdcDeletedAtNotNullCondition(): Condition

    /**
     * Get the window step function row_number() over (partition by primary_key order by
     * cursor_field) as row_number.
     *
     * @param primaryKey list of primary keys
     * @param cursorField cursor field used for ordering
     * @return
     */
    protected abstract fun getRowNumber(
        primaryKey: List<ColumnId>,
        cursorField: Optional<ColumnId>
    ): Field<Int>

    protected open val dslContext: DSLContext
        get() = DSL.using(dialect)

    /**
     * build jooq fields for final table with customers columns first and then meta columns.
     *
     * @param columns
     * @param metaColumns
     * @return
     */
    @VisibleForTesting
    fun buildFinalTableFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        metaColumns: Map<String, DataType<*>>
    ): List<Field<*>> {
        val fields =
            metaColumns.entries
                .stream()
                .map { metaColumn: Map.Entry<String?, DataType<*>?> ->
                    DSL.field(DSL.quotedName(metaColumn.key), metaColumn.value)
                }
                .collect(Collectors.toList())
        val dataFields =
            columns.entries
                .stream()
                .map { column: Map.Entry<ColumnId?, AirbyteType> ->
                    DSL.field(DSL.quotedName(column.key!!.name), toDialectType(column.value))
                }
                .collect(Collectors.toList())
        dataFields.addAll(fields)
        return dataFields
    }

    /**
     * Use this method to get the final table meta columns with or without _airbyte_meta column.
     *
     * @param includeMetaColumn
     * @return
     */
    open fun getFinalTableMetaColumns(
        includeMetaColumn: Boolean
    ): LinkedHashMap<String, DataType<*>> {
        val metaColumns = LinkedHashMap<String, DataType<*>>()
        metaColumns[JavaBaseConstants.COLUMN_NAME_AB_RAW_ID] =
            SQLDataType.VARCHAR(36).nullable(false)
        metaColumns[JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT] =
            timestampWithTimeZoneType.nullable(false)
        if (includeMetaColumn)
            metaColumns[JavaBaseConstants.COLUMN_NAME_AB_META] = structType.nullable(false)
        return metaColumns
    }

    /**
     * build jooq fields for raw table with type-casted data columns first and then meta columns
     * without _airbyte_meta.
     *
     * @param columns
     * @param metaColumns
     * @return
     */
    @VisibleForTesting
    fun buildRawTableSelectFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        metaColumns: Map<String, DataType<*>>,
        useExpensiveSaferCasting: Boolean
    ): List<Field<*>> {
        val fields =
            metaColumns.entries
                .stream()
                .map { metaColumn: Map.Entry<String?, DataType<*>?> ->
                    DSL.field(DSL.quotedName(metaColumn.key), metaColumn.value)
                }
                .collect(Collectors.toList())
        // Use originalName with non-sanitized characters when extracting data from _airbyte_data
        val dataFields = extractRawDataFields(columns, useExpensiveSaferCasting)
        dataFields.addAll(fields)
        return dataFields
    }

    @VisibleForTesting
    fun rawTableCondition(
        syncMode: DestinationSyncMode,
        isCdcDeletedAtPresent: Boolean,
        minRawTimestamp: Optional<Instant>
    ): Condition {
        var condition: Condition =
            DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)).isNull()
        if (syncMode == DestinationSyncMode.APPEND_DEDUP) {
            if (isCdcDeletedAtPresent) {
                condition = condition.or(cdcDeletedAtNotNullCondition())
            }
        }
        if (minRawTimestamp.isPresent) {
            condition =
                condition.and(
                    DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
                        .gt(formatTimestampLiteral(minRawTimestamp.get())),
                )
        }
        return condition
    }

    override fun createSchema(schema: String): Sql {
        return of(createSchemaSql(schema))
    }

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        // TODO: Use Naming transformer to sanitize these strings with redshift restrictions.
        val finalTableIdentifier = stream.id.finalName + suffix.lowercase(Locale.getDefault())
        if (!force) {
            return of(
                createTableSql(stream.id.finalNamespace, finalTableIdentifier, stream.columns)
            )
        }

        val dropTableStep =
            dslContext.dropTableIfExists(
                DSL.quotedName(stream.id.finalNamespace, finalTableIdentifier)
            )
        if (cascadeDrop) {
            dropTableStep.cascade()
        }

        return transactionally(
            dropTableStep.getSQL(ParamType.INLINED),
            createTableSql(
                stream.id.finalNamespace,
                finalTableIdentifier,
                stream.columns,
            ),
        )
    }

    override fun updateTable(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql {
        // TODO: Add flag to use merge vs insert/delete

        return insertAndDeleteTransaction(
            stream,
            finalSuffix,
            minRawTimestamp,
            useExpensiveSaferCasting,
        )
    }

    protected open fun renameTable(schema: String, originalName: String, newName: String): String =
        dslContext.alterTable(DSL.name(schema, originalName)).renameTo(DSL.name(newName)).sql

    override fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql {
        val dropTableStep =
            dslContext.dropTableIfExists(DSL.name(stream.finalNamespace, stream.finalName))
        if (cascadeDrop) {
            dropTableStep.cascade()
        }
        return transactionally(
            dropTableStep.getSQL(ParamType.INLINED),
            renameTable(stream.finalNamespace, stream.finalName + finalSuffix, stream.finalName)
        )
    }

    override fun migrateFromV1toV2(
        streamId: StreamId,
        namespace: String,
        tableName: String,
    ): Sql {
        val rawTableName = DSL.name(streamId.rawNamespace, streamId.rawName)
        val dsl = dslContext
        return transactionally(
            dsl.createSchemaIfNotExists(streamId.rawNamespace).sql,
            dsl.dropTableIfExists(rawTableName).sql,
            createV2RawTableFromV1Table(rawTableName, namespace, tableName),
        )
    }

    protected open fun createV2RawTableFromV1Table(
        rawTableName: Name,
        namespace: String,
        tableName: String
    ) =
        dslContext
            .createTable(rawTableName)
            .column(
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                SQLDataType.VARCHAR(36).nullable(false),
            )
            .column(
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                timestampWithTimeZoneType.nullable(false),
            )
            .column(
                JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
                timestampWithTimeZoneType.nullable(true),
            )
            .column(JavaBaseConstants.COLUMN_NAME_DATA, structType.nullable(false))
            .column(JavaBaseConstants.COLUMN_NAME_AB_META, structType.nullable(true))
            .`as`(
                DSL.select(
                        DSL.field(JavaBaseConstants.COLUMN_NAME_AB_ID)
                            .`as`(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID),
                        DSL.field(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
                            .`as`(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT),
                        DSL.cast(null, timestampWithTimeZoneType)
                            .`as`(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT),
                        DSL.field(JavaBaseConstants.COLUMN_NAME_DATA)
                            .`as`(JavaBaseConstants.COLUMN_NAME_DATA),
                        DSL.cast(null, structType).`as`(JavaBaseConstants.COLUMN_NAME_AB_META),
                    )
                    .from(DSL.table(DSL.name(namespace, tableName))),
            )
            .getSQL(ParamType.INLINED)

    override fun clearLoadedAt(streamId: StreamId): Sql {
        return of(
            dslContext
                .update(DSL.table(DSL.name(streamId.rawNamespace, streamId.rawName)))
                .set(
                    DSL.field(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT),
                    DSL.inline(null as String?),
                )
                .sql,
        )
    }

    @VisibleForTesting
    fun selectFromRawTable(
        schemaName: String,
        tableName: String,
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        metaColumns: Map<String, DataType<*>>,
        condition: Condition,
        useExpensiveSaferCasting: Boolean
    ): SelectConditionStep<Record> {
        val dsl = dslContext
        return dsl.select(buildRawTableSelectFields(columns, metaColumns, useExpensiveSaferCasting))
            .select(buildAirbyteMetaColumn(columns))
            .from(DSL.table(DSL.quotedName(schemaName, tableName)))
            .where(condition)
    }

    @VisibleForTesting
    fun insertIntoFinalTable(
        schemaName: String,
        tableName: String,
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        metaFields: Map<String, DataType<*>>
    ): InsertValuesStepN<Record> {
        val dsl = dslContext
        return dsl.insertInto(DSL.table(DSL.quotedName(schemaName, tableName)))
            .columns(buildFinalTableFields(columns, metaFields))
    }

    private fun insertAndDeleteTransaction(
        streamConfig: StreamConfig,
        finalSuffix: String?,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql {
        val finalSchema = streamConfig.id.finalNamespace
        val finalTable =
            streamConfig.id.finalName + (finalSuffix?.lowercase(Locale.getDefault()) ?: "")
        val rawSchema = streamConfig.id.rawNamespace
        val rawTable = streamConfig.id.rawName

        // Poor person's guarantee of ordering of fields by using same source of ordered list of
        // columns to
        // generate fields.
        val rawTableRowsWithCast =
            DSL.name(TYPING_CTE_ALIAS)
                .`as`(
                    selectFromRawTable(
                        rawSchema,
                        rawTable,
                        streamConfig.columns,
                        getFinalTableMetaColumns(false),
                        rawTableCondition(
                            streamConfig.destinationSyncMode,
                            streamConfig.columns.containsKey(cdcDeletedAtColumn),
                            minRawTimestamp,
                        ),
                        useExpensiveSaferCasting,
                    ),
                )
        val finalTableFields =
            buildFinalTableFields(streamConfig.columns, getFinalTableMetaColumns(true))
        val rowNumber = getRowNumber(streamConfig.primaryKey, streamConfig.cursor)
        val filteredRows =
            DSL.name(NUMBERED_ROWS_CTE_ALIAS)
                .`as`(DSL.select(DSL.asterisk(), rowNumber).from(rawTableRowsWithCast))

        // Used for append-dedupe mode.
        val insertStmtWithDedupe =
            insertIntoFinalTable(
                    finalSchema,
                    finalTable,
                    streamConfig.columns,
                    getFinalTableMetaColumns(true),
                )
                .select(
                    DSL.with(rawTableRowsWithCast)
                        .with(filteredRows)
                        .select(finalTableFields)
                        .from(filteredRows)
                        .where(
                            DSL.field(DSL.name(ROW_NUMBER_COLUMN_NAME), Int::class.java).eq(1),
                        ), // Can refer by CTE.field but no use since we don't strongly type
                    // them.
                    )
                .getSQL(ParamType.INLINED)

        // Used for append and overwrite modes.
        val insertStmt =
            insertIntoFinalTable(
                    finalSchema,
                    finalTable,
                    streamConfig.columns,
                    getFinalTableMetaColumns(true),
                )
                .select(
                    DSL.with(rawTableRowsWithCast)
                        .select(finalTableFields)
                        .from(rawTableRowsWithCast),
                )
                .getSQL(ParamType.INLINED)
        val deleteStmt =
            deleteFromFinalTable(
                finalSchema,
                finalTable,
                streamConfig.primaryKey,
                streamConfig.cursor,
            )
        val deleteCdcDeletesStmt =
            if (streamConfig.columns.containsKey(cdcDeletedAtColumn))
                deleteFromFinalTableCdcDeletes(finalSchema, finalTable)
            else ""
        val checkpointStmt = checkpointRawTable(rawSchema, rawTable, minRawTimestamp)

        if (streamConfig.destinationSyncMode != DestinationSyncMode.APPEND_DEDUP) {
            return transactionally(insertStmt, checkpointStmt)
        }

        // For append-dedupe
        return transactionally(
            insertStmtWithDedupe,
            deleteStmt,
            deleteCdcDeletesStmt,
            checkpointStmt,
        )
    }

    protected fun createSchemaSql(namespace: String): String {
        val dsl = dslContext
        val createSchemaSql = dsl.createSchemaIfNotExists(DSL.quotedName(namespace))
        return createSchemaSql.sql
    }

    protected fun createTableSql(
        namespace: String,
        tableName: String,
        columns: LinkedHashMap<ColumnId, AirbyteType>
    ): String {
        val dsl = dslContext
        val createTableSql =
            dsl.createTable(DSL.quotedName(namespace, tableName))
                .columns(buildFinalTableFields(columns, getFinalTableMetaColumns(true)))
        return createTableSql.sql
    }

    protected fun beginTransaction(): String {
        return "BEGIN"
    }

    protected fun commitTransaction(): String {
        return "COMMIT"
    }

    private fun commitTransactionInternal(): String {
        return commitTransaction() + ";"
    }

    private fun deleteFromFinalTable(
        schemaName: String,
        tableName: String,
        primaryKeys: List<ColumnId>,
        cursor: Optional<ColumnId>
    ): String {
        val dsl = dslContext
        // Unknown type doesn't play well with where .. in (select..)
        val airbyteRawId: Field<Any> =
            DSL.field(DSL.quotedName(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID))
        val rowNumber = getRowNumber(primaryKeys, cursor)
        return dsl.deleteFrom(DSL.table(DSL.quotedName(schemaName, tableName)))
            .where(
                airbyteRawId.`in`(
                    DSL.select(airbyteRawId)
                        .from(
                            DSL.select(airbyteRawId, rowNumber)
                                .from(DSL.table(DSL.quotedName(schemaName, tableName)))
                                .asTable("airbyte_ids"),
                        )
                        .where(DSL.field(DSL.name(ROW_NUMBER_COLUMN_NAME)).ne(1)),
                ),
            )
            .getSQL(ParamType.INLINED)
    }

    private fun deleteFromFinalTableCdcDeletes(schema: String, tableName: String): String {
        val dsl = dslContext
        return dsl.deleteFrom(DSL.table(DSL.quotedName(schema, tableName)))
            .where(DSL.field(DSL.quotedName(cdcDeletedAtColumn.name)).isNotNull())
            .getSQL(ParamType.INLINED)
    }

    private fun checkpointRawTable(
        schemaName: String,
        tableName: String,
        minRawTimestamp: Optional<Instant>
    ): String {
        val dsl = dslContext
        var extractedAtCondition = DSL.noCondition()
        if (minRawTimestamp.isPresent) {
            extractedAtCondition =
                extractedAtCondition.and(
                    DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
                        .gt(formatTimestampLiteral(minRawTimestamp.get())),
                )
        }
        return dsl.update<Record>(DSL.table(DSL.quotedName(schemaName, tableName)))
            .set<Any>(
                DSL.field(DSL.quotedName(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)),
                currentTimestamp(),
            )
            .where(DSL.field(DSL.quotedName(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)).isNull())
            .and(extractedAtCondition)
            .getSQL(ParamType.INLINED)
    }

    protected open fun castedField(
        field: Field<*>,
        type: AirbyteType,
        useExpensiveSaferCasting: Boolean
    ): Field<*> {
        if (type is AirbyteProtocolType) {
            return castedField(field, type, useExpensiveSaferCasting)
        }

        // Redshift SUPER can silently cast an array type to struct and vice versa.
        return when (type.typeName) {
            Struct.TYPE,
            UnsupportedOneOf.TYPE -> DSL.cast(field, structType)
            Array.TYPE -> DSL.cast(field, arrayType)
            Union.TYPE -> castedField(field, (type as Union).chooseType(), useExpensiveSaferCasting)
            else -> throw IllegalArgumentException("Unsupported AirbyteType: $type")
        }
    }

    protected open fun castedField(
        field: Field<*>,
        type: AirbyteProtocolType,
        useExpensiveSaferCasting: Boolean
    ): Field<*> {
        return DSL.cast(field, toDialectType(type))
    }

    protected open fun currentTimestamp(): Field<Timestamp> {
        return DSL.currentTimestamp()
    }

    /**
     * Some destinations (mysql) can't handle timestamps in ISO8601 format with 'Z' suffix. This
     * method allows subclasses to format timestamps according to destination-specific needs.
     */
    protected open fun formatTimestampLiteral(instant: Instant): String {
        return instant.toString()
    }

    companion object {
        const val ROW_NUMBER_COLUMN_NAME: String = "row_number"
        private const val TYPING_CTE_ALIAS = "intermediate_data"
        private const val NUMBERED_ROWS_CTE_ALIAS = "numbered_rows"
    }
}
