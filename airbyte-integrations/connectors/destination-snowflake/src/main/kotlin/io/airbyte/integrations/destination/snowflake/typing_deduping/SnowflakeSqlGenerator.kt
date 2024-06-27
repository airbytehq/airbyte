/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.google.common.annotations.VisibleForTesting
import com.google.common.collect.ImmutableList
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.concat
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.of
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.transactionally
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.SOFT_RESET_SUFFIX
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabaseUtils
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.time.Instant
import java.util.*
import java.util.stream.Collectors
import org.apache.commons.lang3.StringUtils
import org.apache.commons.text.StringSubstitutor

class SnowflakeSqlGenerator(private val retentionPeriodDays: Int) : SqlGenerator {
    private val cdcDeletedAtColumn = buildColumnId("_ab_cdc_deleted_at")

    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        return StreamId(
            escapeSqlIdentifier(namespace).uppercase(Locale.getDefault()),
            escapeSqlIdentifier(name).uppercase(Locale.getDefault()),
            escapeSqlIdentifier(rawNamespaceOverride),
            escapeSqlIdentifier(concatenateRawTableName(namespace, name)),
            namespace,
            name
        )
    }

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun buildColumnId(name: String, suffix: String?): ColumnId {
        val escapedName =
            prefixReservedColumnName(escapeSqlIdentifier(name).uppercase(Locale.getDefault())) +
                suffix!!.uppercase(Locale.getDefault())
        return ColumnId(escapedName, name, escapedName)
    }

    fun toDialectType(type: AirbyteType): String {
        if (type is AirbyteProtocolType) {
            return toDialectType(type)
        } else if (type is Struct) {
            // TODO should this+array just be VARIANT?
            return "OBJECT"
        } else if (type is Array) {
            return "ARRAY"
        } else if (type is UnsupportedOneOf) {
            return "VARIANT"
        } else if (type is Union) {
            val typeWithPrecedence: AirbyteType = type.chooseType()
            // typeWithPrecedence is never a Union, so this recursion is safe.
            return toDialectType(typeWithPrecedence)
        }

        // Literally impossible; AirbyteType is a sealed interface.
        throw IllegalArgumentException("Unsupported AirbyteType: $type")
    }

    private fun toDialectType(airbyteProtocolType: AirbyteProtocolType): String {
        return SnowflakeDatabaseUtils.toSqlTypeName(airbyteProtocolType)
    }

    override fun createSchema(schema: String): Sql {
        return of(
            StringSubstitutor(java.util.Map.of("schema", StringUtils.wrap(schema, QUOTE)))
                .replace("CREATE SCHEMA IF NOT EXISTS \${schema};")
        )
    }

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        val columnDeclarations =
            stream.columns.entries
                .stream()
                .map { column: Map.Entry<ColumnId, AirbyteType> ->
                    "," + column.key.name(QUOTE) + " " + toDialectType(column.value)
                }
                .collect(Collectors.joining("\n"))
        val forceCreateTable = if (force) "OR REPLACE" else ""

        return of(
            StringSubstitutor(
                    java.util.Map.of(
                        "final_table_id",
                        stream.id.finalTableId(QUOTE, suffix.uppercase(Locale.getDefault())),
                        "force_create_table",
                        forceCreateTable,
                        "column_declarations",
                        columnDeclarations,
                        "retention_period_days",
                        retentionPeriodDays
                    )
                )
                .replace(
                    """
            CREATE ${'$'}{force_create_table} TABLE ${'$'}{final_table_id} (
              "_AIRBYTE_RAW_ID" TEXT NOT NULL,
              "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
              "_AIRBYTE_META" VARIANT NOT NULL,
              "_AIRBYTE_GENERATION_ID" INTEGER
              ${'$'}{column_declarations}
            ) data_retention_time_in_days = ${'$'}{retention_period_days};
            
            """.trimIndent()
                )
        )
    }

    override fun updateTable(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql {
        val insertNewRecords =
            insertNewRecords(
                stream,
                finalSuffix,
                stream.columns,
                minRawTimestamp,
                useExpensiveSaferCasting
            )
        var dedupFinalTable = ""
        var cdcDeletes = ""
        if (stream.destinationSyncMode == DestinationSyncMode.APPEND_DEDUP) {
            dedupFinalTable =
                dedupFinalTable(stream.id, finalSuffix, stream.primaryKey, stream.cursor)
            cdcDeletes = cdcDeletes(stream, finalSuffix)
        }
        val commitRawTable = commitRawTable(stream.id)

        return transactionally(insertNewRecords, dedupFinalTable, cdcDeletes, commitRawTable)
    }

    private fun extractAndCast(
        column: ColumnId,
        airbyteType: AirbyteType,
        useTryCast: Boolean
    ): String {
        return cast(
            "\"_airbyte_data\":\"" + escapeJsonIdentifier(column.originalName) + "\"",
            airbyteType,
            useTryCast
        )
    }

    private fun cast(sqlExpression: String, airbyteType: AirbyteType, useTryCast: Boolean): String {
        val castMethod = if (useTryCast) "TRY_CAST" else "CAST"
        if (airbyteType is Union) {
            // This is guaranteed to not be a Union, so we won't recurse infinitely
            val chosenType: AirbyteType = airbyteType.chooseType()
            return cast(sqlExpression, chosenType, useTryCast)
        } else if (airbyteType === AirbyteProtocolType.TIME_WITH_TIMEZONE) {
            // We're using TEXT for this type, so need to explicitly check the string format.
            // There's a bunch of ways we could do this; this regex is approximately correct and
            // easy to
            // implement.
            // It'll match anything like HH:MM:SS[.SSS](Z|[+-]HH[:]MM), e.g.:
            // 12:34:56Z
            // 12:34:56.7+08:00
            // 12:34:56.7890123-0800
            // 12:34:56-08
            return StringSubstitutor(java.util.Map.of("expression", sqlExpression))
                .replace(
                    """
          CASE
            WHEN NOT ((${'$'}{expression})::TEXT REGEXP '\\d{1,2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}(:?\\d{2})?)')
              THEN NULL
            ELSE ${'$'}{expression}
          END
          
          """.trimIndent()
                )
        } else {
            val dialectType = toDialectType(airbyteType)
            return when (dialectType) {
                "TIMESTAMP_TZ" ->
                    StringSubstitutor(
                            java.util.Map.of("expression", sqlExpression, "cast", castMethod)
                        )
                        .replace( // Handle offsets in +/-HHMM and +/-HH formats
                            // The four cases, in order, match:
                            // 2023-01-01T12:34:56-0800
                            // 2023-01-01T12:34:56-08
                            // 2023-01-01T12:34:56.7890123-0800
                            // 2023-01-01T12:34:56.7890123-08
                            // And the ELSE will try to handle everything else.
                            """
            CASE
              WHEN (${'$'}{expression})::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}'
                THEN TO_TIMESTAMP_TZ((${'$'}{expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
              WHEN (${'$'}{expression})::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}'
                THEN TO_TIMESTAMP_TZ((${'$'}{expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZH')
              WHEN (${'$'}{expression})::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}'
                THEN TO_TIMESTAMP_TZ((${'$'}{expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
              WHEN (${'$'}{expression})::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}'
                THEN TO_TIMESTAMP_TZ((${'$'}{expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
              ELSE ${'$'}{cast}((${'$'}{expression})::TEXT AS TIMESTAMP_TZ)
            END
            
            """.trimIndent()
                        )
                "VARIANT" -> sqlExpression
                "OBJECT" ->
                    StringSubstitutor(java.util.Map.of("expression", sqlExpression))
                        .replace(
                            """
            CASE
              WHEN TYPEOF(${'$'}{expression}) != 'OBJECT'
                THEN NULL
              ELSE ${'$'}{expression}
            END
            
            """.trimIndent()
                        )
                "ARRAY" ->
                    StringSubstitutor(java.util.Map.of("expression", sqlExpression))
                        .replace(
                            """
            CASE
              WHEN TYPEOF(${'$'}{expression}) != 'ARRAY'
                THEN NULL
              ELSE ${'$'}{expression}
            END
            
            """.trimIndent()
                        )
                "TEXT" -> "(($sqlExpression)::text)"
                else -> "$castMethod(($sqlExpression)::text as $dialectType)"
            }
        }
    }

    @VisibleForTesting
    fun insertNewRecords(
        stream: StreamConfig,
        finalSuffix: String,
        streamColumns: LinkedHashMap<ColumnId, AirbyteType>,
        minRawTimestamp: Optional<Instant>,
        useTryCast: Boolean
    ): String {
        val columnList =
            streamColumns.keys
                .stream()
                .map { quotedColumnId: ColumnId -> quotedColumnId.name(QUOTE) + "," }
                .collect(Collectors.joining("\n"))
        val extractNewRawRecords = extractNewRawRecords(stream, minRawTimestamp, useTryCast)

        return StringSubstitutor(
                java.util.Map.of(
                    "final_table_id",
                    stream.id.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault())),
                    "column_list",
                    columnList,
                    "extractNewRawRecords",
                    extractNewRawRecords
                )
            )
            .replace(
                """
            INSERT INTO ${'$'}{final_table_id}
            (
            ${'$'}{column_list}
              "_AIRBYTE_META",
              "_AIRBYTE_RAW_ID",
              "_AIRBYTE_EXTRACTED_AT",
              "_AIRBYTE_GENERATION_ID"
            )
            ${'$'}{extractNewRawRecords};
            """.trimIndent()
            )
    }

    private fun extractNewRawRecords(
        stream: StreamConfig,
        minRawTimestamp: Optional<Instant>,
        useTryCast: Boolean
    ): String {
        val columnCasts =
            stream.columns.entries
                .stream()
                .map { col: Map.Entry<ColumnId, AirbyteType> ->
                    extractAndCast(col.key, col.value, useTryCast) +
                        " as " +
                        col.key.name(QUOTE) +
                        ","
                }
                .collect(Collectors.joining("\n"))
        val columnErrors =
            stream.columns.entries
                .stream()
                .map { col: Map.Entry<ColumnId, AirbyteType> ->
                    StringSubstitutor(
                            java.util.Map.of(
                                "raw_col_name",
                                escapeJsonIdentifier(col.key.originalName),
                                "printable_col_name",
                                escapeSingleQuotedString(col.key.originalName),
                                "col_type",
                                toDialectType(col.value),
                                "json_extract",
                                extractAndCast(col.key, col.value, useTryCast)
                            )
                        )
                        .replace( // TYPEOF returns "NULL_VALUE" for a JSON null and "NULL" for a
                            // SQL null
                            """
                CASE
                  WHEN (TYPEOF("_airbyte_data":"${'$'}{raw_col_name}") NOT IN ('NULL', 'NULL_VALUE'))
                    AND (${'$'}{json_extract} IS NULL)
                    THEN OBJECT_CONSTRUCT('field', '${'$'}{printable_col_name}', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
                  ELSE NULL
                END
                """.trimIndent()
                        )
                }
                .collect(Collectors.joining(",\n"))
        val columnList =
            stream.columns.keys
                .stream()
                .map { quotedColumnId: ColumnId -> quotedColumnId.name(QUOTE) + "," }
                .collect(Collectors.joining("\n"))
        val extractedAtCondition = buildExtractedAtCondition(minRawTimestamp)

        if (stream.destinationSyncMode == DestinationSyncMode.APPEND_DEDUP) {
            var cdcConditionalOrIncludeStatement = ""
            if (stream.columns.containsKey(cdcDeletedAtColumn)) {
                cdcConditionalOrIncludeStatement =
                    """
                                           OR (
                                             "_airbyte_loaded_at" IS NOT NULL
                                             AND TYPEOF("_airbyte_data":"_ab_cdc_deleted_at") NOT IN ('NULL', 'NULL_VALUE')
                                           )
                                           
                                           """.trimIndent()
            }

            val pkList =
                stream.primaryKey
                    .stream()
                    .map { columnId: ColumnId -> columnId.name(QUOTE) }
                    .collect(Collectors.joining(","))
            val cursorOrderClause =
                stream.cursor
                    .map { cursorId: ColumnId -> cursorId.name(QUOTE) + " DESC NULLS LAST," }
                    .orElse("")

            return StringSubstitutor(
                    java.util.Map.of(
                        "raw_table_id",
                        stream.id.rawTableId(QUOTE),
                        "column_casts",
                        columnCasts,
                        "column_errors",
                        columnErrors,
                        "cdcConditionalOrIncludeStatement",
                        cdcConditionalOrIncludeStatement,
                        "extractedAtCondition",
                        extractedAtCondition,
                        "column_list",
                        columnList,
                        "pk_list",
                        pkList,
                        "cursor_order_clause",
                        cursorOrderClause,
                        "airbyte_extracted_at_utc",
                        airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\"")
                    )
                )
                .replace(
                    """
              WITH intermediate_data AS (
                SELECT
              ${'$'}{column_casts}
              ARRAY_COMPACT(
              ARRAY_CAT(
                CASE WHEN "_airbyte_meta":"changes" IS NOT NULL
                THEN "_airbyte_meta":"changes"
                ELSE ARRAY_CONSTRUCT()
                END,
              ARRAY_CONSTRUCT(${'$'}{column_errors}))) as "_airbyte_cast_errors",
                "_airbyte_raw_id",
                ${'$'}{airbyte_extracted_at_utc} as "_airbyte_extracted_at",
                "_airbyte_meta",
                "_airbyte_generation_id"
                FROM ${'$'}{raw_table_id}
                WHERE (
                    "_airbyte_loaded_at" IS NULL
                    ${'$'}{cdcConditionalOrIncludeStatement}
                  ) ${'$'}{extractedAtCondition}
              ), new_records AS (
                SELECT
                ${'$'}{column_list}
                  CASE WHEN "_airbyte_meta" IS NOT NULL 
                  THEN OBJECT_INSERT("_airbyte_meta", 'changes', "_airbyte_cast_errors", true) 
                  ELSE OBJECT_CONSTRUCT('changes', "_airbyte_cast_errors") 
                  END AS "_AIRBYTE_META",
                  "_airbyte_raw_id" AS "_AIRBYTE_RAW_ID",
                  "_airbyte_extracted_at" AS "_AIRBYTE_EXTRACTED_AT",
                  "_airbyte_generation_id" AS "_AIRBYTE_GENERATION_ID"
                FROM intermediate_data
              ), numbered_rows AS (
                SELECT *, row_number() OVER (
                  PARTITION BY ${'$'}{pk_list} ORDER BY ${'$'}{cursor_order_clause} "_AIRBYTE_EXTRACTED_AT" DESC
                ) AS row_number
                FROM new_records
              )
              SELECT ${'$'}{column_list} "_AIRBYTE_META", "_AIRBYTE_RAW_ID", "_AIRBYTE_EXTRACTED_AT", "_AIRBYTE_GENERATION_ID"
              FROM numbered_rows
              WHERE row_number = 1
              """.trimIndent()
                )
        } else {
            return StringSubstitutor(
                    java.util.Map.of(
                        "raw_table_id",
                        stream.id.rawTableId(QUOTE),
                        "column_casts",
                        columnCasts,
                        "column_errors",
                        columnErrors,
                        "extractedAtCondition",
                        extractedAtCondition,
                        "column_list",
                        columnList,
                        "airbyte_extracted_at_utc",
                        airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\"")
                    )
                )
                .replace(
                    """
              WITH intermediate_data AS (
                SELECT
              ${'$'}{column_casts}
              ARRAY_COMPACT(
              ARRAY_CAT(
                CASE WHEN "_airbyte_meta":"changes" IS NOT NULL
                THEN "_airbyte_meta":"changes"
                ELSE ARRAY_CONSTRUCT()
                END,
              ARRAY_CONSTRUCT(${'$'}{column_errors}))) as "_airbyte_cast_errors",
                "_airbyte_raw_id",
                ${'$'}{airbyte_extracted_at_utc} as "_airbyte_extracted_at",
                "_airbyte_meta",
                "_airbyte_generation_id"
                FROM ${'$'}{raw_table_id}
                WHERE
                  "_airbyte_loaded_at" IS NULL
                  ${'$'}{extractedAtCondition}
              )
              SELECT
              ${'$'}{column_list}
                CASE WHEN "_airbyte_meta" IS NOT NULL 
                THEN OBJECT_INSERT("_airbyte_meta", 'changes', "_airbyte_cast_errors", true) 
                ELSE OBJECT_CONSTRUCT('changes', "_airbyte_cast_errors") 
                END AS "_AIRBYTE_META",
                "_airbyte_raw_id" AS "_AIRBYTE_RAW_ID",
                "_airbyte_extracted_at" AS "_AIRBYTE_EXTRACTED_AT",
                "_airbyte_generation_id" AS "_AIRBYTE_GENERATION_ID"
              FROM intermediate_data
              """.trimIndent()
                )
        }
    }

    @VisibleForTesting
    fun dedupFinalTable(
        id: StreamId,
        finalSuffix: String,
        primaryKey: List<ColumnId>,
        cursor: Optional<ColumnId>
    ): String {
        val pkList =
            primaryKey
                .stream()
                .map { columnId: ColumnId -> columnId.name(QUOTE) }
                .collect(Collectors.joining(","))
        val cursorOrderClause =
            cursor
                .map { cursorId: ColumnId -> cursorId.name(QUOTE) + " DESC NULLS LAST," }
                .orElse("")

        return StringSubstitutor(
                java.util.Map.of(
                    "final_table_id",
                    id.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault())),
                    "pk_list",
                    pkList,
                    "cursor_order_clause",
                    cursorOrderClause,
                    "airbyte_extracted_at_utc",
                    airbyteExtractedAtUtcForced("\"_AIRBYTE_EXTRACTED_AT\"")
                )
            )
            .replace(
                """
            DELETE FROM ${'$'}{final_table_id}
            WHERE "_AIRBYTE_RAW_ID" IN (
              SELECT "_AIRBYTE_RAW_ID" FROM (
                SELECT "_AIRBYTE_RAW_ID", row_number() OVER (
                  PARTITION BY ${'$'}{pk_list} ORDER BY ${'$'}{cursor_order_clause} ${'$'}{airbyte_extracted_at_utc} DESC
                ) as row_number FROM ${'$'}{final_table_id}
              )
              WHERE row_number != 1
            );
            
            """.trimIndent()
            )
    }

    private fun cdcDeletes(stream: StreamConfig, finalSuffix: String): String {
        if (stream.destinationSyncMode != DestinationSyncMode.APPEND_DEDUP) {
            return ""
        }
        if (!stream.columns.containsKey(cdcDeletedAtColumn)) {
            return ""
        }

        // we want to grab IDs for deletion from the raw table (not the final table itself) to hand
        // out-of-order record insertions after the delete has been registered
        return StringSubstitutor(
                java.util.Map.of(
                    "final_table_id",
                    stream.id.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault()))
                )
            )
            .replace(
                """
            DELETE FROM ${'$'}{final_table_id}
            WHERE _AB_CDC_DELETED_AT IS NOT NULL;
            
            """.trimIndent()
            )
    }

    @VisibleForTesting
    fun commitRawTable(id: StreamId): String {
        return StringSubstitutor(java.util.Map.of("raw_table_id", id.rawTableId(QUOTE)))
            .replace(
                """
            UPDATE ${'$'}{raw_table_id}
            SET "_airbyte_loaded_at" = CURRENT_TIMESTAMP()
            WHERE "_airbyte_loaded_at" IS NULL
            ;
            """.trimIndent()
            )
    }

    override fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql {
        val substitutor =
            StringSubstitutor(
                java.util.Map.of(
                    "final_table",
                    stream.finalTableId(QUOTE),
                    "tmp_final_table",
                    stream.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault()))
                )
            )
        return transactionally(
            substitutor.replace("DROP TABLE IF EXISTS \${final_table};"),
            substitutor.replace("ALTER TABLE \${tmp_final_table} RENAME TO \${final_table};")
        )
    }

    override fun prepareTablesForSoftReset(stream: StreamConfig): Sql {
        return concat(
            createTable(stream, SOFT_RESET_SUFFIX.uppercase(Locale.getDefault()), true),
            clearLoadedAt(stream.id)
        )
    }

    override fun clearLoadedAt(streamId: StreamId): Sql {
        return of(
            StringSubstitutor(java.util.Map.of("raw_table_id", streamId.rawTableId(QUOTE)))
                .replace(
                    """
                 UPDATE ${'$'}{raw_table_id} SET "_airbyte_loaded_at" = NULL;
                 
                 """.trimIndent()
                )
        )
    }

    override fun migrateFromV1toV2(streamId: StreamId, namespace: String, tableName: String): Sql {
        // In the SQL below, the v2 values are quoted to preserve their case while the v1 values are
        // intentionally _not_ quoted. This is to preserve the implicit upper-casing behavior in v1.
        return of(
            StringSubstitutor(
                    java.util.Map.of(
                        "raw_table_name",
                        streamId.rawTableId(QUOTE),
                        "raw_id",
                        JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                        "extracted_at",
                        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                        "loaded_at",
                        JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
                        "meta",
                        JavaBaseConstants.COLUMN_NAME_AB_META,
                        "generation_id",
                        JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
                        "data",
                        JavaBaseConstants.COLUMN_NAME_DATA,
                        "v1_raw_id",
                        JavaBaseConstants.COLUMN_NAME_AB_ID,
                        "emitted_at",
                        JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                        "v1_raw_table",
                        java.lang.String.join(".", namespace, tableName)
                    )
                )
                .replace(
                    """
                CREATE OR REPLACE TABLE ${'$'}{raw_table_name} (
                  "${'$'}{raw_id}" VARCHAR PRIMARY KEY,
                  "${'$'}{extracted_at}" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
                  "${'$'}{loaded_at}" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
                  "${'$'}{data}" VARIANT,
                  "${'$'}{meta}" VARIANT,
                  "${'$'}{generation_id}" INTEGER
                )
                data_retention_time_in_days = 0
                AS (
                  SELECT
                    ${'$'}{v1_raw_id} AS "${'$'}{raw_id}",
                    ${'$'}{emitted_at} AS "${'$'}{extracted_at}",
                    CAST(NULL AS TIMESTAMP WITH TIME ZONE) AS "${'$'}{loaded_at}",
                    PARSE_JSON(${'$'}{data}) AS "${'$'}{data}",
                    CAST(NULL AS VARIANT) AS "${'$'}{meta}",
                    CAST(NULL AS INTEGER) AS "${'$'}{generation_id}",
                  FROM ${'$'}{v1_raw_table}
                )
                ;
                
                """.trimIndent()
                )
        )
    }

    companion object {
        const val QUOTE: String = "\""

        // See https://docs.snowflake.com/en/sql-reference/reserved-keywords.html
        // and
        // https://github.com/airbytehq/airbyte/blob/f226503bd1d4cd9c7412b04d47de584523988443/airbyte-integrations/bases/base-normalization/normalization/transform_catalog/reserved_keywords.py
        private val RESERVED_COLUMN_NAMES: List<String> =
            ImmutableList.of(
                "CURRENT_DATE",
                "CURRENT_TIME",
                "CURRENT_TIMESTAMP",
                "CURRENT_USER",
                "LOCALTIME",
                "LOCALTIMESTAMP"
            )

        private fun airbyteExtractedAtUtcForced(sqlExpression: String): String {
            return StringSubstitutor(java.util.Map.of("expression", sqlExpression))
                .replace(
                    """
        TIMESTAMPADD(
          HOUR,
          EXTRACT(timezone_hour from ${'$'}{expression}),
          TIMESTAMPADD(
            MINUTE,
            EXTRACT(timezone_minute from ${'$'}{expression}),
            CONVERT_TIMEZONE('UTC', ${'$'}{expression})
          )
        )
        
        """.trimIndent()
                )
        }

        private fun buildExtractedAtCondition(minRawTimestamp: Optional<Instant>): String {
            return minRawTimestamp
                .map { ts: Instant ->
                    " AND " +
                        airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\"") +
                        " > '" +
                        ts +
                        "'"
                }
                .orElse("")
        }

        /**
         * Snowflake json object access is done using double-quoted strings, e.g. `SELECT
         * "_airbyte_data":"foo"`. As such, we need to escape double-quotes in the field name.
         */
        @JvmStatic
        fun escapeJsonIdentifier(identifier: String): String {
            // Note that we don't need to escape backslashes here!
            // The only special character in an identifier is the double-quote, which needs to be
            // doubled.
            return identifier.replace("\"", "\"\"")
        }

        /**
         * SQL identifiers are also double-quoted strings. They have slightly more stringent
         * requirements than JSON field identifiers.
         *
         * This method is separate from [.escapeJsonIdentifier] because we need to retain the
         * original field name for JSON access, e.g. `SELECT "_airbyte_data":"${FOO" AS "__FOO"`.
         */
        fun escapeSqlIdentifier(inputIdentifier: String): String {
            // Snowflake scripting language does something weird when the `${` bigram shows up in
            // the script
            // so replace these with something else.
            // For completeness, if we trigger this, also replace closing curly braces with
            // underscores.
            var identifier = inputIdentifier
            if (identifier.contains("\${")) {
                identifier = identifier.replace("$", "_").replace("{", "_").replace("}", "_")
            }

            return escapeJsonIdentifier(identifier)
        }

        private fun prefixReservedColumnName(columnName: String): String {
            return if (
                RESERVED_COLUMN_NAMES.stream().anyMatch { k: String ->
                    k.equals(columnName, ignoreCase = true)
                }
            )
                "_$columnName"
            else columnName
        }

        fun escapeSingleQuotedString(str: String): String {
            return str.replace("\\", "\\\\").replace("'", "\\'")
        }
    }
}
