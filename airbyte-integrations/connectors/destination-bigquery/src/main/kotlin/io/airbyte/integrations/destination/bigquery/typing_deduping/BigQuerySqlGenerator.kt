/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.orchestration.db.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingSqlGenerator
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer
import java.time.Instant
import java.util.*
import java.util.stream.Collectors
import org.apache.commons.lang3.StringUtils

/**
 * @param projectId
 * @param datasetLocation This is technically redundant with [BigQueryDatabaseHandler] setting the
 * query execution location, but let's be explicit since this is typically a compliance requirement.
 */
class BigQuerySqlGenerator(private val projectId: String?, private val datasetLocation: String?) :
    TypingDedupingSqlGenerator {
    private fun extractAndCast(
        columnName: String,
        airbyteType: AirbyteType,
        forceSafeCast: Boolean
    ): String {
        if (airbyteType is UnionType && airbyteType.isLegacyUnion) {
            // This is guaranteed to not be a Union, so we won't recurse infinitely
            val chosenType: AirbyteType = airbyteType.chooseType()
            return extractAndCast(columnName, chosenType, forceSafeCast)
        }
        val jsonPathEscapedColumnName = escapeColumnNameForJsonPath(columnName)

        if (airbyteType.isObject) {
            // We need to validate that the struct is actually a struct.
            // Note that struct columns are actually nullable in two ways. For a column `foo`:
            // {foo: null} and {} are both valid, and are both written to the final table as a SQL
            // NULL (_not_ a
            // JSON null).
            // JSON_QUERY(JSON'{}', '$."foo"') returns a SQL null.
            // JSON_QUERY(JSON'{"foo": null}', '$."foo"') returns a JSON null.
            return """
                   PARSE_JSON(CASE
                     WHEN JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"') IS NULL
                       OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"'), wide_number_mode=>'round')) != 'object'
                       THEN NULL
                     ELSE JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"')
                   END, wide_number_mode=>'round')
                   """.trimIndent()
        }

        if (airbyteType.isArray) {
            // Much like the Struct case above, arrays need special handling.
            return """
                   PARSE_JSON(CASE
                     WHEN JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"') IS NULL
                       OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"'), wide_number_mode=>'round')) != 'array'
                       THEN NULL
                     ELSE JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"')
                   END, wide_number_mode=>'round')
                   """.trimIndent()
        }

        if (airbyteType is UnionType || airbyteType is UnknownType) {
            // JSON_QUERY returns a SQL null if the field contains a JSON null, so we actually parse
            // the
            // airbyte_data to json
            // and json_query it directly (which preserves nulls correctly).
            return """JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '${'$'}."$jsonPathEscapedColumnName"')"""
        }

        if (airbyteType is StringType) {
            // Special case String to only use json value for type string and parse the json for
            // others
            // Naive json_value returns NULL for object/array values and json_query adds escaped
            // quotes to the string.
            return """
                   (CASE
                     WHEN JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"') IS NULL
                       OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"'), wide_number_mode=>'round')) != 'string'
                       THEN JSON_QUERY(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"')
                     ELSE
                     JSON_VALUE(`_airbyte_data`, '${'$'}."$jsonPathEscapedColumnName"')
                   END)
                   """.trimIndent()
        }

        val dialectType = toDialectType(airbyteType)
        val baseTyping = """JSON_VALUE(`_airbyte_data`, '$."$jsonPathEscapedColumnName"')"""
        return if (dialectType == StandardSQLTypeName.STRING) {
            // json_value implicitly returns a string, so we don't need to cast it.
            baseTyping
        } else {
            // SAFE_CAST is actually a massive performance hit, so we should skip it if we can.
            cast(baseTyping, dialectType.name, forceSafeCast)
        }
    }

    override fun createFinalTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        replace: Boolean
    ): Sql {
        val columnDeclarations = columnsAndTypes(stream, columnNameMapping)
        val clusterConfig =
            clusteringColumns(stream, columnNameMapping)
                .stream()
                .map { c: String? -> StringUtils.wrap(c, QUOTE) }
                .collect(Collectors.joining(", "))
        val finalTableId = tableName.toPrettyString(QUOTE, finalTableSuffix)
        return Sql.separately(
            listOfNotNull(
                // CREATE OR REPLACE TABLE exists,
                // but still returns an error if the new table has a different
                // partitioning/clustering scheme.
                // So we'll explicitly drop+create the table instead.
                if (replace) {
                    """DROP TABLE IF EXISTS `$projectId`.$finalTableId"""
                } else {
                    null
                },
                """
                CREATE TABLE `$projectId`.$finalTableId (
                  _airbyte_raw_id STRING NOT NULL,
                  _airbyte_extracted_at TIMESTAMP NOT NULL,
                  _airbyte_meta JSON NOT NULL,
                  _airbyte_generation_id INTEGER,
                  $columnDeclarations
                )
                PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
                CLUSTER BY $clusterConfig;
                """.trimIndent(),
            )
        )
    }

    private fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): String {
        return stream.schema
            .asColumns()
            .map { (fieldName, type) ->
                val columnName = columnNameMapping[fieldName]!!
                val typeName = toDialectType(type.type).name
                "`$columnName` $typeName"
            }
            .joinToString(",\n")
    }

    override fun prepareTablesForSoftReset(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
    ): Sql {
        // Bigquery can't run DDL in a transaction, so these are separate transactions.
        return Sql.concat(
            // If a previous sync failed to delete the soft reset temp table (unclear why
            // this happens),
            // AND this sync is trying to change the clustering config, then we need to manually
            // drop the soft
            // reset temp table.
            // Even though we're using CREATE OR REPLACE TABLE, bigquery will still complain
            // about the
            // clustering config being changed.
            // So we explicitly drop the soft reset temp table first.
            dropTableIfExists(tableNames.finalTableName!!, TableNames.SOFT_RESET_SUFFIX),
            createFinalTable(
                stream,
                tableNames.finalTableName!!,
                columnNameMapping,
                TableNames.SOFT_RESET_SUFFIX,
                true
            ),
            clearLoadedAt(stream, tableNames.rawTableName!!)
        )
    }

    private fun dropTableIfExists(
        finalTableName: TableName,
        suffix: String,
    ): Sql {
        val tableId = finalTableName.toPrettyString(QUOTE, suffix)
        return Sql.of("""DROP TABLE IF EXISTS `$projectId`.$tableId;""")
    }

    override fun clearLoadedAt(stream: DestinationStream, rawTableName: TableName): Sql {
        val rawTableId = rawTableName.toPrettyString(QUOTE)
        return Sql.of(
            """UPDATE `$projectId`.$rawTableId SET _airbyte_loaded_at = NULL WHERE 1=1;"""
        )
    }

    override fun updateFinalTable(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
        finalTableSuffix: String,
        maxProcessedTimestamp: Instant?,
        useExpensiveSaferCasting: Boolean,
    ): Sql {
        val handleNewRecords =
            if (stream.importType is Dedupe) {
                upsertNewRecords(
                    stream,
                    tableNames,
                    columnNameMapping,
                    finalTableSuffix,
                    useExpensiveSaferCasting,
                    maxProcessedTimestamp
                )
            } else {
                insertNewRecords(
                    stream,
                    tableNames,
                    columnNameMapping,
                    finalTableSuffix,
                    useExpensiveSaferCasting,
                    maxProcessedTimestamp
                )
            }
        val commitRawTable = commitRawTable(tableNames.rawTableName!!, maxProcessedTimestamp)

        return Sql.transactionally(handleNewRecords, commitRawTable)
    }

    private fun insertNewRecords(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
        finalSuffix: String,
        forceSafeCasting: Boolean,
        minRawTimestamp: Instant?,
    ): String {
        val columnList: String =
            stream.schema
                .asColumns()
                .keys
                .stream()
                .map { fieldName ->
                    val columnName = columnNameMapping[fieldName]!!
                    "`$columnName`,"
                }
                .collect(Collectors.joining("\n"))
        val extractNewRawRecords =
            extractNewRawRecords(
                stream,
                tableNames,
                columnNameMapping,
                forceSafeCasting,
                minRawTimestamp
            )
        val finalTableId = tableNames.finalTableName!!.toPrettyString(QUOTE, finalSuffix)

        return """
               INSERT INTO `$projectId`.$finalTableId
               (
               $columnList
                 _airbyte_meta,
                 _airbyte_raw_id,
                 _airbyte_extracted_at,
                 _airbyte_generation_id
               )
               $extractNewRawRecords;
               """.trimIndent()
    }

    private fun upsertNewRecords(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
        finalSuffix: String,
        forceSafeCasting: Boolean,
        minRawTimestamp: Instant?,
    ): String {
        val importType = stream.importType as Dedupe
        val pkEquivalent =
            importType.primaryKey.joinToString(" AND ") { fieldPath ->
                val fieldName = fieldPath.first()
                val columnName = columnNameMapping[fieldName]!!
                """(target_table.`$columnName` = new_record.`$columnName` OR (target_table.`$columnName` IS NULL AND new_record.`$columnName` IS NULL))"""
            }

        val columnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "`$columnName`,"
            }
        val newRecordColumnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "new_record.`$columnName`,"
            }
        val extractNewRawRecords =
            extractNewRawRecords(
                stream,
                tableNames,
                columnNameMapping,
                forceSafeCasting,
                minRawTimestamp
            )

        val cursorComparison: String
        if (importType.cursor.isNotEmpty()) {
            val cursorFieldName = importType.cursor.first()
            val cursorColumnName = columnNameMapping[cursorFieldName]!!
            val cursor = "`$cursorColumnName`"
            // Build a condition for "new_record is more recent than target_table":
            cursorComparison = // First, compare the cursors.
            ("""
             (
               target_table.$cursor < new_record.$cursor
               OR (target_table.$cursor = new_record.$cursor AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)
               OR (target_table.$cursor IS NULL AND new_record.$cursor IS NULL AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)
               OR (target_table.$cursor IS NULL AND new_record.$cursor IS NOT NULL)
             )
             """.trimIndent())
        } else {
            // If there's no cursor, then we just take the most-recently-emitted record
            cursorComparison =
                "target_table._airbyte_extracted_at < new_record._airbyte_extracted_at"
        }

        val cdcDeleteClause: String
        val cdcSkipInsertClause: String
        if (stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
            // Execute CDC deletions if there's already a record
            cdcDeleteClause =
                "WHEN MATCHED AND new_record._ab_cdc_deleted_at IS NOT NULL AND $cursorComparison THEN DELETE"
            // And skip insertion entirely if there's no matching record.
            // (This is possible if a single T+D batch contains both an insertion and deletion for
            // the same PK)
            cdcSkipInsertClause = "AND new_record._ab_cdc_deleted_at IS NULL"
        } else {
            cdcDeleteClause = ""
            cdcSkipInsertClause = ""
        }

        val columnAssignments: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val column = columnNameMapping[fieldName]!!
                "`$column` = new_record.`$column`,"
            }
        val finalTableId = tableNames.finalTableName!!.toPrettyString(QUOTE, finalSuffix)

        return """
               MERGE `$projectId`.$finalTableId target_table
               USING (
                 $extractNewRawRecords
               ) new_record
               ON $pkEquivalent
               $cdcDeleteClause
               WHEN MATCHED AND $cursorComparison THEN UPDATE SET
                 $columnAssignments
                 _airbyte_meta = new_record._airbyte_meta,
                 _airbyte_raw_id = new_record._airbyte_raw_id,
                 _airbyte_extracted_at = new_record._airbyte_extracted_at,
                 _airbyte_generation_id = new_record._airbyte_generation_id
               WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT (
                 $columnList
                 _airbyte_meta,
                 _airbyte_raw_id,
                 _airbyte_extracted_at,
                 _airbyte_generation_id
               ) VALUES (
                 $newRecordColumnList
                 new_record._airbyte_meta,
                 new_record._airbyte_raw_id,
                 new_record._airbyte_extracted_at,
                 new_record._airbyte_generation_id
               );
               """.trimIndent()
    }

    /**
     * A SQL SELECT statement that extracts new records from the raw table, casts their columns, and
     * builds their airbyte_meta column.
     *
     * In dedup mode: Also extracts all raw CDC deletion records (for tombstoning purposes) and
     * dedupes the records (since we only need the most-recent record to upsert).
     */
    private fun extractNewRawRecords(
        stream: DestinationStream,
        tableNames: TableNames,
        columnNameMapping: ColumnNameMapping,
        forceSafeCasting: Boolean,
        minRawTimestamp: Instant?,
    ): String {
        val columnCasts: String =
            stream.schema
                .asColumns()
                .map { (fieldName, type) ->
                    val columnName = columnNameMapping[fieldName]!!
                    val extractAndCast = extractAndCast(fieldName, type.type, forceSafeCasting)
                    "$extractAndCast as `$columnName`,"
                }
                .joinToString("\n")
        val columnErrors =
            if (forceSafeCasting) {
                "[" +
                    stream.schema
                        .asColumns()
                        .map { (fieldName, type) ->
                            val rawColName = escapeColumnNameForJsonPath(fieldName)
                            val jsonExtract = extractAndCast(fieldName, type.type, true)
                            // Explicitly parse json here. This is safe because
                            // we're not using the actual value anywhere,
                            // and necessary because json_query
                            """
                            CASE
                              WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '${'$'}."$rawColName"') IS NOT NULL)
                                AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '${'$'}."$rawColName"')) != 'null')
                                AND ($jsonExtract IS NULL)
                                THEN JSON '{"field":"$rawColName","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
                              ELSE NULL
                            END
                            """.trimIndent()
                        }
                        .joinToString(",\n") +
                    "]"
            } else {
                // We're not safe casting, so any error should throw an exception and trigger the
                // safe cast logic
                "[]"
            }

        val columnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "`$columnName`,"
            }
        val extractedAtCondition = buildExtractedAtCondition(minRawTimestamp)

        val rawTableId = tableNames.rawTableName!!.toPrettyString(QUOTE)
        if (stream.importType is Dedupe) {
            val importType = stream.importType as Dedupe
            // When deduping, we need to dedup the raw records. Note the row_number() invocation in
            // the SQL
            // statement. Do the same extract+cast CTE + airbyte_meta construction as in non-dedup
            // mode, but
            // then add a row_number column so that we only take the most-recent raw record for each
            // PK.

            // We also explicitly include old CDC deletion records, which act as tombstones to
            // correctly delete
            // out-of-order records.

            var cdcConditionalOrIncludeStatement = ""
            if (stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
                cdcConditionalOrIncludeStatement =
                    """
                    OR (
                      _airbyte_loaded_at IS NOT NULL
                      AND JSON_VALUE(`_airbyte_data`, '${'$'}._ab_cdc_deleted_at') IS NOT NULL
                    )
                    """.trimIndent()
            }

            val pkList =
                importType.primaryKey.joinToString(",") { fieldName ->
                    val columnName = columnNameMapping[fieldName.first()]!!
                    "`$columnName`"
                }
            val cursorOrderClause =
                if (importType.cursor.isEmpty()) {
                    ""
                } else if (importType.cursor.size == 1) {
                    val columnName = columnNameMapping[importType.cursor.first()]!!
                    "`$columnName` DESC NULLS LAST,"
                } else {
                    throw UnsupportedOperationException(
                        "Only top-level cursors are supported, got ${importType.cursor}"
                    )
                }

            return """
                   WITH intermediate_data AS (
                     SELECT
                   $columnCasts
                     $columnErrors AS column_errors,
                     _airbyte_raw_id,
                     _airbyte_extracted_at,
                     _airbyte_meta,
                     _airbyte_generation_id
                     FROM `$projectId`.$rawTableId
                     WHERE (
                         _airbyte_loaded_at IS NULL
                         $cdcConditionalOrIncludeStatement
                       ) $extractedAtCondition
                   ), new_records AS (
                     SELECT
                     $columnList
                       to_json(json_set(
                         coalesce(parse_json(_airbyte_meta), JSON'{}'),
                         '${'$'}.changes',
                         json_array_append(
                           coalesce(json_query(parse_json(_airbyte_meta), '${'$'}.changes'), JSON'[]'),
                           '${'$'}',
                           COALESCE((SELECT ARRAY_AGG(unnested_column_errors IGNORE NULLS) FROM UNNEST(column_errors) unnested_column_errors), [])
                          )
                       )) as _airbyte_meta,
                       _airbyte_raw_id,
                       _airbyte_extracted_at,
                       _airbyte_generation_id
                     FROM intermediate_data
                   ), numbered_rows AS (
                     SELECT *, row_number() OVER (
                       PARTITION BY $pkList ORDER BY $cursorOrderClause `_airbyte_extracted_at` DESC
                     ) AS row_number
                     FROM new_records
                   )
                   SELECT $columnList _airbyte_meta, _airbyte_raw_id, _airbyte_extracted_at, _airbyte_generation_id
                   FROM numbered_rows
                   WHERE row_number = 1
                   """.trimIndent()
        } else {
            // When not deduplicating, we just need to handle type casting.
            // Extract+cast the not-yet-loaded records in a CTE, then select that CTE and build
            // airbyte_meta.

            return """
                   WITH intermediate_data AS (
                     SELECT
                   $columnCasts
                     $columnErrors AS column_errors,
                     _airbyte_raw_id,
                     _airbyte_extracted_at,
                     _airbyte_meta,
                     _airbyte_generation_id
                     FROM `$projectId`.$rawTableId
                     WHERE
                       _airbyte_loaded_at IS NULL
                       $extractedAtCondition
                   )
                   SELECT
                   $columnList
                     to_json(json_set(
                         coalesce(parse_json(_airbyte_meta), JSON'{}'),
                         '${'$'}.changes',
                         json_array_append(
                           coalesce(json_query(parse_json(_airbyte_meta), '${'$'}.changes'), JSON'[]'),
                           '${'$'}',
                           COALESCE((SELECT ARRAY_AGG(unnested_column_errors IGNORE NULLS) FROM UNNEST(column_errors) unnested_column_errors), [])
                          )
                       )) as _airbyte_meta,
                     _airbyte_raw_id,
                     _airbyte_extracted_at,
                     _airbyte_generation_id
                   FROM intermediate_data
                   """.trimIndent()
        }
    }

    @VisibleForTesting
    fun commitRawTable(rawTableName: TableName, minRawTimestamp: Instant?): String {
        val rawTableId = rawTableName.toPrettyString(QUOTE)
        val extractedAtCondition = buildExtractedAtCondition(minRawTimestamp)
        return """
               UPDATE `$projectId`.$rawTableId
               SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
               WHERE `_airbyte_loaded_at` IS NULL
                 $extractedAtCondition
               ;
               """.trimIndent()
    }

    override fun overwriteFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        finalTableSuffix: String,
    ): Sql {
        val finalTableId = finalTableName.toPrettyString(QUOTE)
        val tempFinalTableId = finalTableName.toPrettyString(QUOTE, finalTableSuffix)
        return Sql.separately(
            "DROP TABLE IF EXISTS `$projectId`.$finalTableId;",
            "ALTER TABLE `$projectId`.$tempFinalTableId RENAME TO `${finalTableName.name}`;"
        )
    }

    /**
     * Does two things: escape single quotes (for use inside sql string literals),and escape double
     * quotes (for use inside JSON paths). For example, if a column name is foo'bar"baz, then we
     * want to end up with something like `SELECT JSON_QUERY(..., '$."foo\'bar\\"baz"')`. Note the
     * single-backslash for single-quotes (needed for SQL) and the double-backslash for
     * double-quotes (needed for JSON path).
     */
    private fun escapeColumnNameForJsonPath(stringContents: String): String {
        // This is not a place of honor.
        return stringContents // Consider the JSON blob {"foo\\bar": 42}.
            // This is an object with key foo\bar.
            // The JSONPath for this is $."foo\\bar" (i.e. 2 backslashes to represent the single
            // backslash in the key).
            // When we represent that path as a SQL string, the backslashes are doubled (to 4):
            // '$."foo\\\\bar"'
            // And we're writing that in a Java string, so we have to type out 8 backslashes:
            // "'$.\"foo\\\\\\\\bar\"'"
            .replace("\\", "\\\\\\\\") // Similar situation here:
            // a literal " needs to be \" in a JSONPath: $."foo\"bar"
            // which is \\" in a SQL string: '$."foo\\"bar"'
            // The backslashes become \\\\ in java, and the quote becomes \": "'$.\"foo\\\\\"bar\"'"
            .replace(
                "\"",
                "\\\\\""
            ) // Here we're escaping a SQL string, so we only need a single backslash (which is 2,
            // because Java).
            .replace("'", "\\'")
    }

    companion object {
        const val QUOTE: String = "`"
        val nameTransformer = BigQuerySQLNameTransformer()

        fun toDialectType(type: AirbyteType): StandardSQLTypeName =
            when (type) {
                BooleanType -> StandardSQLTypeName.BOOL
                DateType -> StandardSQLTypeName.DATE
                IntegerType -> StandardSQLTypeName.INT64
                NumberType -> StandardSQLTypeName.NUMERIC
                StringType -> StandardSQLTypeName.STRING
                TimeTypeWithTimezone -> StandardSQLTypeName.STRING
                TimeTypeWithoutTimezone -> StandardSQLTypeName.TIME
                TimestampTypeWithTimezone -> StandardSQLTypeName.TIMESTAMP
                TimestampTypeWithoutTimezone -> StandardSQLTypeName.DATETIME
                is ArrayType,
                ArrayTypeWithoutSchema,
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> StandardSQLTypeName.JSON
                is UnionType ->
                    if (type.isLegacyUnion) {
                        toDialectType(type.chooseType())
                    } else {
                        StandardSQLTypeName.JSON
                    }
                is UnknownType -> StandardSQLTypeName.JSON
            }

        fun clusteringColumns(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping
        ): List<String> {
            val clusterColumns: MutableList<String> = ArrayList()
            if (stream.importType is Dedupe) {
                // We're doing de-duping, therefore we have a primary key.
                // Cluster on the first 3 PK columns since BigQuery only allows up to 4 clustering
                // columns,
                // and we're always clustering on _airbyte_extracted_at
                (stream.importType as Dedupe).primaryKey.stream().limit(3).forEach {
                    pk: List<String> ->
                    clusterColumns.add(columnNameMapping[pk.first()]!!)
                }
            }
            clusterColumns.add("_airbyte_extracted_at")
            return clusterColumns
        }

        private fun buildExtractedAtCondition(minRawTimestamp: Instant?): String {
            return minRawTimestamp?.let { ts: Instant -> " AND _airbyte_extracted_at > '$ts'" }
                ?: ""
        }

        private fun cast(content: String, asType: String, useSafeCast: Boolean): String {
            val open = if (useSafeCast) "SAFE_CAST(" else "CAST("
            return wrap(open, "$content as $asType", ")")
        }

        private fun wrap(open: String, content: String, close: String): String {
            return open + content + close
        }
    }
}
