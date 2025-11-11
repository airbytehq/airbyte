/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.of
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.separately
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.transactionally
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import java.time.Instant
import java.util.*
import java.util.stream.Collectors
import org.jooq.Condition
import org.jooq.DataType
import org.jooq.Field
import org.jooq.Name
import org.jooq.Record
import org.jooq.SQLDialect
import org.jooq.SortField
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.DSL.field
import org.jooq.impl.DSL.name
import org.jooq.impl.DSL.quotedName
import org.jooq.impl.DSL.rowNumber
import org.jooq.impl.DSL.sql
import org.jooq.impl.DefaultDataType
import org.jooq.impl.SQLDataType
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * The `TeradataSqlGenerator` class provides methods to generate SQL for creating tables, inserting,
 * deleting, and transforming data in a Teradata-based destination. It extends `JdbcSqlGenerator`
 * and uses JOOQ for building SQL queries.
 */
class TeradataSqlGenerator() : JdbcSqlGenerator(namingTransformer = StandardNameTransformer()) {

    /**
     * Creates a schema in Teradata.
     *
     * @param schema The name of the schema to create.
     * @return A SQL statement to create the schema.
     */
    override fun createSchema(schema: String): Sql {
        return of(
            String.format(
                "CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;",
                schema,
            ),
        )
    }
    /**
     * Returns the data type used for array columns in Teradata.
     *
     * @return The `JSON_TYPE` data type.
     */
    override val arrayType: DataType<*>
        get() = JSON_TYPE
    /**
     * Returns the SQL dialect for Teradata.
     *
     * @return The `DEFAULT` SQL dialect.
     */
    override val dialect: SQLDialect
        get() = SQLDialect.DEFAULT
    /**
     * Returns the struct data type used for struct columns in Teradata.
     *
     * @return The `JSON_TYPE` data type.
     */
    override val structType: DataType<*>
        get() = JSON_TYPE
    /**
     * Returns the widest data type used in Teradata.
     *
     * @return The `JSON_TYPE` data type.
     */
    override val widestType: DataType<*>
        get() = JSON_TYPE
    /**
     * Builds the Airbyte meta column SQL expression.
     *
     * @param columns The columns in the stream, used to construct the expression.
     * @return The SQL field expression to extract the Airbyte meta column.
     */
    override fun buildAirbyteMetaColumn(columns: LinkedHashMap<ColumnId, AirbyteType>): Field<*> {
        return field(
                sql(
                    """COALESCE($COLUMN_NAME_AB_META, CAST('{"changes":[]}' AS JSON))""",
                ),
            )
            .`as`(COLUMN_NAME_AB_META)
    }

    /**
     * Generates the condition for CDC `deleted_at` field in Teradata.
     *
     * @return The SQL condition for checking if the CDC `deleted_at` column is not null.
     */
    override fun cdcDeletedAtNotNullCondition(): Condition {
        return field(name(COLUMN_NAME_AB_LOADED_AT))
            .isNotNull()
            .and(extractColumnAsJson(cdcDeletedAtColumn).notEqual("null"))
    }
    /**
     * Helper method to extract a column as JSON from the data field.
     *
     * @param column The column to extract from the JSON field.
     * @return The extracted column value as a `Field` of type `Any`.
     */
    private fun extractColumnAsJson(column: ColumnId): Field<Any> {
        return field(
            (("cast(" + name(COLUMN_NAME_DATA)) +
                ".JSONExtractValue('$." +
                field(column.originalName)) + "') as VARCHAR(100) )",
        )
    }
    /**
     * Extracts raw data fields from the given columns.
     *
     * @param columns The columns to extract raw data fields for.
     * @param useExpensiveSaferCasting Flag indicating whether to use expensive casting for certain
     * fields.
     * @return A list of SQL fields representing the extracted raw data.
     */
    override fun extractRawDataFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        useExpensiveSaferCasting: Boolean
    ): MutableList<Field<*>> {
        val fields: MutableList<Field<*>> = ArrayList()
        columns.forEach { (key, value) ->
            if (
                value == AirbyteProtocolType.UNKNOWN ||
                    value.typeName == "STRUCT" ||
                    value.typeName == "ARRAY"
            ) {
                fields.add(
                    field(
                            (("cast(" + name(COLUMN_NAME_DATA)) +
                                ".JSONExtract('$." +
                                field(
                                    key.originalName,
                                )) + "') as " + toDialectType(value) + ")",
                        )
                        .`as`(key.name),
                )
            } else if (
                value == AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE ||
                    value == AirbyteProtocolType.TIME_WITH_TIMEZONE ||
                    value == AirbyteProtocolType.DATE ||
                    value == AirbyteProtocolType.TIME_WITH_TIMEZONE ||
                    value == AirbyteProtocolType.TIME_WITHOUT_TIMEZONE
            ) {
                fields.add(
                    field(
                            "CASE " +
                                "WHEN TRYCAST(" +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractValue('$." +
                                field(
                                    key.originalName,
                                ) +
                                "') AS " +
                                toDialectType(value) +
                                ") IS NOT NULL " +
                                "THEN TRYCAST(" +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractValue('$." +
                                field(
                                    key.originalName,
                                ) +
                                "') AS " +
                                toDialectType(value) +
                                ") " +
                                "ELSE NULL END",
                        )
                        .`as`(key.name),
                )
            } else if (value == AirbyteProtocolType.STRING) {
                fields.add(
                    field(
                            "CASE " +
                                "WHEN CAST(" +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractValue('$." +
                                field(key.originalName) +
                                "') AS " +
                                toDialectType(value) +
                                ") IS NOT NULL " +
                                "THEN CAST(" +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractValue('$." +
                                field(key.originalName) +
                                "') AS " +
                                toDialectType(value) +
                                ") " +
                                "WHEN CAST(" +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractLargeValue('$." +
                                field(key.originalName) +
                                "') AS " +
                                toDialectType(value) +
                                ") IS NOT NULL " +
                                "THEN CAST(" +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractLargeValue('$." +
                                field(key.originalName) +
                                "') AS " +
                                toDialectType(value) +
                                ") " +
                                "ELSE NULL " +
                                "END"
                        )
                        .`as`(key.name)
                )
            } else if (value == AirbyteProtocolType.BOOLEAN) {
                fields.add(
                    field(
                            ("CASE WHEN" +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractValue('$." +
                                field(
                                    key.originalName,
                                ) +
                                "') = 'TRUE' THEN 1 WHEN " +
                                name(COLUMN_NAME_DATA) +
                                ".JSONExtractValue('$." +
                                field(
                                    key.originalName,
                                ) +
                                "') = 'FALSE' THEN 0 END")
                        )
                        .`as`(key.name),
                )
            } else {
                fields.add(
                    field(
                            (("cast(" + name(COLUMN_NAME_DATA)) +
                                ".JSONExtractValue('$." +
                                field(
                                    key.originalName,
                                )) + "') as " + toDialectType(value) + ")",
                        )
                        .`as`(key.name),
                )
            }
        }
        return fields
    }
    /**
     * Generates a `ROW_NUMBER` SQL expression for the given primary key and cursor field.
     *
     * @param primaryKey The primary key columns.
     * @param cursorField The cursor field for ordering (if available).
     * @return The SQL expression representing the `ROW_NUMBER` function.
     */
    override fun getRowNumber(
        primaryKey: List<ColumnId>,
        cursorField: Optional<ColumnId>
    ): Field<Int> {
        val primaryKeyFields: List<Field<*>> =
            primaryKey
                .stream()
                .map { columnId: ColumnId ->
                    field(
                        quotedName(columnId.name),
                    )
                }
                .collect(Collectors.toList<Field<*>>())
        val orderedFields: MutableList<SortField<Any>> = ArrayList()

        cursorField.ifPresent { columnId ->
            orderedFields.add(
                field(quotedName(columnId.name)).desc().nullsLast(),
            )
        }

        orderedFields.add(field("{0}", quotedName(COLUMN_NAME_AB_EXTRACTED_AT)).desc())
        val query =
            rowNumber()
                .over()
                .partitionBy(primaryKeyFields)
                .orderBy(orderedFields)
                .`as`(ROW_NUMBER_COLUMN_NAME)
        return query
    }
    /**
     * Converts an Airbyte protocol type to the corresponding SQL dialect type. This method maps the
     * Airbyte protocol types to the appropriate SQL data types.
     *
     * @param airbyteProtocolType The Airbyte protocol type to be converted.
     * @return The corresponding SQL dialect type.
     */
    override fun toDialectType(airbyteProtocolType: AirbyteProtocolType): DataType<*> {
        val s =
            when (airbyteProtocolType) {
                AirbyteProtocolType.STRING -> SQLDataType.VARCHAR(10000)
                AirbyteProtocolType.BOOLEAN -> SQLDataType.SMALLINT
                // Airbyte handling BigInt as Integer and Teradata raising error when BigInt came
                // for Integer like - 9223372036854775807
                AirbyteProtocolType.INTEGER -> SQLDataType.BIGINT
                AirbyteProtocolType.NUMBER -> SQLDataType.FLOAT
                else -> super.toDialectType(airbyteProtocolType)
            }
        return s
    }
    /**
     * Creates a new table based on the provided stream configuration. If the `force` parameter is
     * true, the existing table will be dropped before creating the new one. Otherwise, the table
     * will be created without dropping the existing one.
     *
     * @param stream The stream configuration that contains table details such as name, namespace,
     * and columns.
     * @param suffix The suffix to append to the table name when creating the final table
     * identifier.
     * @param force A flag indicating whether to force the dropping of an existing table before
     * creating the new one.
     * @return The SQL statement to create the table, potentially including a drop table statement
     * if `force` is true.
     */
    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {

        val finalTableIdentifier: String =
            stream.id.finalName + suffix.lowercase(Locale.getDefault())

        if (!force) {
            return separately(
                createTableSql(
                    stream.id.finalNamespace,
                    finalTableIdentifier,
                    stream.columns,
                ),
            )
        }

        val sl =
            separately(
                java.lang.String.format(
                    "DROP TABLE %s.%s;",
                    stream.id.finalNamespace,
                    finalTableIdentifier,
                ),
                createTableSql(
                    stream.id.finalNamespace,
                    finalTableIdentifier,
                    stream.columns,
                ),
            )
        return sl
    }
    /**
     * Overwrites the final table by renaming the old table to a new name. This is typically used
     * when transitioning from one version of the table schema to another.
     *
     * @param stream The stream identifier containing the final table namespace and name.
     * @param finalSuffix The suffix to append to the table name for the final table.
     * @return The SQL statement to drop the old table and rename the new one.
     */
    override fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql {
        val spaceName: String = stream.finalNamespace
        val tableName: String = stream.finalName + finalSuffix
        val newTableName: String = stream.finalName

        val query =
            separately(
                String.format("DROP TABLE %s.%s;", spaceName, newTableName),
                String.format(
                    "RENAME TABLE %s.%s TO %s.%s;",
                    spaceName,
                    tableName,
                    spaceName,
                    newTableName,
                ),
            )
        return query
    }
    /**
     * Migrates a table from version 1 to version 2 by creating a new V2 table from the data in the
     * V1 table. The migration process involves creating a new table with adjusted columns and data
     * types.
     *
     * @param streamId The identifier of the stream to be migrated.
     * @param namespace The namespace where the table resides.
     * @param tableName The name of the table to migrate.
     * @return The SQL statement to perform the migration.
     */
    override fun migrateFromV1toV2(streamId: StreamId, namespace: String, tableName: String): Sql {
        val rawTableName: Name = name(streamId.rawNamespace, streamId.rawName)
        return transactionally(
            createV2RawTableFromV1Table(rawTableName, namespace, tableName),
        )
    }
    /**
     * Creates a V2 raw table from the V1 table by selecting and adjusting the required columns,
     * including casting specific columns to the appropriate data types.
     *
     * @param rawTableName The name of the raw table to be created.
     * @param namespace The namespace where the table will be created.
     * @param tableName The name of the V1 table from which to create the V2 raw table.
     * @return The SQL statement to create the V2 raw table.
     */
    public override fun createV2RawTableFromV1Table(
        rawTableName: Name,
        namespace: String,
        tableName: String
    ): String {
        val query =
            java.lang.String.format(
                "CREATE TABLE %s AS ( SELECT %s %s, %s %s, CAST(NULL AS TIMESTAMP WITH TIME ZONE) %s, %s %s, CAST(NULL AS JSON) %s, 0 %s FROM %s.%s) WITH DATA",
                rawTableName,
                COLUMN_NAME_AB_ID,
                COLUMN_NAME_AB_RAW_ID,
                COLUMN_NAME_EMITTED_AT,
                COLUMN_NAME_AB_EXTRACTED_AT,
                COLUMN_NAME_AB_LOADED_AT,
                COLUMN_NAME_DATA,
                COLUMN_NAME_DATA,
                COLUMN_NAME_AB_META,
                COLUMN_NAME_AB_GENERATION_ID,
                namespace,
                tableName,
            )
        return query
    }
    /**
     * Generates the SQL for performing an insert and delete transaction in Teradata. This method
     * handles both append and append-dedupe modes. It inserts data into a final table, deletes old
     * or unnecessary records, and ensures the correct ordering of records for deduplication if
     * necessary.
     *
     * @param streamConfig The stream configuration which includes information about the stream,
     * ```
     *                     primary key, cursor, columns, and post-import action.
     * @param finalSuffix
     * ```
     * An optional suffix that can be added to the final table name.
     * @param minRawTimestamp An optional minimum timestamp used for filtering raw data during
     * insert.
     * @param useExpensiveSaferCasting A flag indicating whether to use expensive, safer casting
     * ```
     *                                 for certain data types during data extraction.
     * @return
     * ```
     * The generated SQL wrapped in a transaction for inserting and deleting data.
     * ```
     *         The SQL will differ depending on whether the import type is APPEND or APPEND_DEDUPE.
     *
     * @throws SQLException
     * ```
     * If there is an error generating the SQL for the transaction.
     */
    override fun insertAndDeleteTransaction(
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
                            streamConfig.postImportAction,
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
                .`as`(DSL.select(finalTableFields).select(rowNumber).from(rawTableRowsWithCast))
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
        if (streamConfig.postImportAction == ImportType.APPEND) {
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
    /**
     * Creates a SQL update statement that updates the `AB_LOADED_AT` column of the given table. The
     * `AB_LOADED_AT` column is set to the current timestamp where it is currently `NULL`, and the
     * `AB_EXTRACTED_AT` column is greater than the provided minimum timestamp if present.
     *
     * @param schemaName The schema name where the table resides.
     * @param tableName The table name to be updated.
     * @param minRawTimestamp An optional minimum timestamp for filtering the rows to be updated.
     * @return The SQL update statement for checkpointing the raw table.
     */
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
    /**
     * Creates a SQL delete statement that removes rows from the final table where the
     * `CDC_DELETED_AT` column is not `NULL`. This is typically used to handle deletions in CDC
     * (Change Data Capture) scenarios.
     *
     * @param schema The schema name where the table resides.
     * @param tableName The table name from which rows will be deleted.
     * @return The SQL delete statement to remove CDC deleted rows from the final table.
     */
    private fun deleteFromFinalTableCdcDeletes(schema: String, tableName: String): String {
        val dsl = dslContext
        return dsl.deleteFrom(DSL.table(DSL.quotedName(schema, tableName)))
            .where(DSL.field(DSL.quotedName(cdcDeletedAtColumn.name)).isNotNull())
            .getSQL(ParamType.INLINED)
    }
    /**
     * Creates a SQL delete statement that deletes rows from the final table based on the primary
     * keys and cursor. This delete operation ensures that only non-duplicate or non-eligible rows
     * are deleted. The rows are identified using the `AB_RAW_ID` field and the row number based on
     * the provided primary keys.
     *
     * @param schemaName The schema name where the table resides.
     * @param tableName The table name from which rows will be deleted.
     * @param primaryKeys The list of primary key columns used for deduplication and identifying
     * rows.
     * @param cursor An optional cursor column that helps in filtering rows to delete.
     * @return The SQL delete statement to delete specific rows from the final table based on
     * primary keys and cursor.
     */
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

    companion object {

        private val LOGGER: Logger = LoggerFactory.getLogger(TeradataSqlGenerator::class.java)
        // Alias used for intermediate data in SQL queries
        const val TYPING_CTE_ALIAS = "intermediate_data"
        // Alias used for rows with assigned numbers in SQL queries
        const val NUMBERED_ROWS_CTE_ALIAS = "numbered_rows"
        // Default JSON type used in SQL statements
        val JSON_TYPE: DefaultDataType<Any> =
            DefaultDataType(
                null,
                Any::class.java,
                "json",
            )
    }
}
