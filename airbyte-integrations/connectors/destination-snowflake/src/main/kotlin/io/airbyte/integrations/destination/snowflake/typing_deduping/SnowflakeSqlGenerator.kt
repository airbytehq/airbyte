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
        return of("""CREATE SCHEMA IF NOT EXISTS "$schema";""")
    }

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        val columnDeclarations =
            stream.columns
                .map { (col, type) -> ", ${col.name(QUOTE)} ${toDialectType(type)}" }
                .joinToString("\n")
        val forceCreateTable = if (force) "OR REPLACE" else ""

        val createTableSql =
            """
            |CREATE $forceCreateTable TABLE ${stream.id.finalTableId(QUOTE, suffix.uppercase(Locale.getDefault()))} (
            |  "_AIRBYTE_RAW_ID" TEXT NOT NULL,
            |  "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
            |  "_AIRBYTE_META" VARIANT NOT NULL,
            |  "_AIRBYTE_GENERATION_ID" INTEGER
            |  $columnDeclarations
            |) data_retention_time_in_days = $retentionPeriodDays;
        """.trimMargin()

        return of(createTableSql)
    }

    override fun updateTable(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql {
        val insertNewRecords =
            insertNewRecords(stream, finalSuffix, minRawTimestamp, useExpensiveSaferCasting)
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
            return """
                |CASE 
                |  WHEN NOT ((${sqlExpression})::TEXT REGEXP '\\d{1,2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}(:?\\d{2})?)') 
                |  THEN NULL 
                |  ELSE $sqlExpression 
                |END
            """.trimMargin()
        } else {
            return when (val dialectType = toDialectType(airbyteType)) {
                "TIMESTAMP_TZ" ->
                    // Handle offsets in +/-HHMM and +/-HH formats
                    // The four cases, in order, match:
                    // 2023-01-01T12:34:56-0800
                    // 2023-01-01T12:34:56-08
                    // 2023-01-01T12:34:56.7890123-0800
                    // 2023-01-01T12:34:56.7890123-08
                    // And the ELSE will try to handle everything else.
                    """
                        |CASE
                        |  WHEN ($sqlExpression)::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}'
                        |    THEN TO_TIMESTAMP_TZ(($sqlExpression)::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
                        |  WHEN ($sqlExpression)::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}'
                        |    THEN TO_TIMESTAMP_TZ(($sqlExpression)::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZH')
                        |  WHEN ($sqlExpression)::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}'
                        |    THEN TO_TIMESTAMP_TZ(($sqlExpression)::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
                        |  WHEN ($sqlExpression)::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}'
                        |    THEN TO_TIMESTAMP_TZ(($sqlExpression)::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
                        |  ELSE $castMethod(($sqlExpression)::TEXT AS TIMESTAMP_TZ)
                        |END
                    """.trimMargin()
                "VARIANT" -> sqlExpression
                "OBJECT" ->
                    """
                        |CASE 
                        |  WHEN TYPEOF($sqlExpression) != 'OBJECT'
                        |    THEN NULL 
                        |  ELSE $sqlExpression 
                        |END
                    """.trimMargin()
                "ARRAY" ->
                    """
                        |CASE 
                        |  WHEN TYPEOF($sqlExpression) != 'ARRAY' 
                        |    THEN NULL 
                        |  ELSE $sqlExpression 
                        |END
                    """.trimMargin()
                "TEXT" -> "(($sqlExpression)::text)"
                else -> "$castMethod(($sqlExpression)::text as $dialectType)"
            }
        }
    }

    @VisibleForTesting
    fun insertNewRecords(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useTryCast: Boolean
    ): String {
        val columnList = stream.columns.keys.joinToString("\n") { "${it.name(QUOTE)}," }
        val extractNewRawRecords = extractNewRawRecords(stream, minRawTimestamp, useTryCast)

        return """
            |INSERT INTO ${stream.id.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault()))}(
            |  $columnList
            |  "_AIRBYTE_META",
            |  "_AIRBYTE_RAW_ID",
            |  "_AIRBYTE_EXTRACTED_AT",
            |  "_AIRBYTE_GENERATION_ID"
            |)
            |$extractNewRawRecords;
            |""".trimMargin()
    }

    private fun extractNewRawRecords(
        stream: StreamConfig,
        minRawTimestamp: Optional<Instant>,
        useTryCast: Boolean
    ): String {
        val columnCasts =
            stream.columns.entries.joinToString("\n") { col: Map.Entry<ColumnId, AirbyteType> ->
                "${extractAndCast(col.key, col.value, useTryCast)} as ${col.key.name(QUOTE)} ,"
            }
        val columnErrors =
            stream.columns
                .map { col ->
                    """
            |CASE
            |  WHEN (TYPEOF("_airbyte_data":"${escapeJsonIdentifier(col.key.originalName)}") NOT IN ('NULL', 'NULL_VALUE'))
            |    AND (${extractAndCast(col.key, col.value, useTryCast)} IS NULL)
            |    THEN OBJECT_CONSTRUCT('field', '${escapeSingleQuotedString(col.key.originalName)}', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            |  ELSE NULL
            |END
            |""".trimMargin()
                }
                .joinToString(", \n")
        val columnList = stream.columns.keys.joinToString("\n") { "${it.name(QUOTE)}," }
        val extractedAtCondition = buildExtractedAtCondition(minRawTimestamp)

        if (stream.destinationSyncMode == DestinationSyncMode.APPEND_DEDUP) {
            var cdcConditionalOrIncludeStatement = ""
            if (stream.columns.containsKey(cdcDeletedAtColumn)) {
                cdcConditionalOrIncludeStatement =
                    """
                    |OR ("_airbyte_loaded_at" IS NOT NULL AND TYPEOF("_airbyte_data":"_ab_cdc_deleted_at") NOT IN ('NULL', 'NULL_VALUE'))
                    |""".trimMargin()
            }

            val pkList = stream.primaryKey.joinToString { it.name(QUOTE) }
            val cursorOrderClause =
                stream.cursor
                    .map { cursorId: ColumnId -> "${cursorId.name(QUOTE)} DESC NULLS LAST," }
                    .orElse("")

            return """
                |WITH intermediate_data AS (
                |  SELECT
                |    $columnCasts
                |    ARRAY_COMPACT(
                |      ARRAY_CAT(
                |        CASE WHEN "_airbyte_meta":"changes" IS NOT NULL
                |          THEN "_airbyte_meta":"changes"
                |          ELSE ARRAY_CONSTRUCT()
                |        END,
                |      ARRAY_CONSTRUCT($columnErrors))
                |    ) as "_airbyte_cast_errors",
                |    "_airbyte_raw_id",
                |    ${airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\"")} as "_airbyte_extracted_at",
                |    "_airbyte_meta",
                |    "_airbyte_generation_id"
                |  FROM 
                |  ${stream.id.rawTableId(QUOTE)}
                |  WHERE (
                |    "_airbyte_loaded_at" IS NULL
                |    $cdcConditionalOrIncludeStatement
                |    ) $extractedAtCondition
                |), new_records AS (
                |  SELECT
                |    $columnList
                |    CASE WHEN "_airbyte_meta" IS NOT NULL 
                |      THEN OBJECT_INSERT("_airbyte_meta", 'changes', "_airbyte_cast_errors", true) 
                |      ELSE OBJECT_CONSTRUCT('changes', "_airbyte_cast_errors") 
                |    END AS "_AIRBYTE_META",
                |    "_airbyte_raw_id" AS "_AIRBYTE_RAW_ID",
                |    "_airbyte_extracted_at" AS "_AIRBYTE_EXTRACTED_AT",
                |    "_airbyte_generation_id" AS "_AIRBYTE_GENERATION_ID"
                |  FROM intermediate_data
                |), numbered_rows AS (
                |  SELECT *, row_number() 
                |    OVER (PARTITION BY $pkList ORDER BY $cursorOrderClause "_AIRBYTE_EXTRACTED_AT" DESC) AS row_number
                |  FROM 
                |  new_records
                |)
                |SELECT 
                |  $columnList 
                |  "_AIRBYTE_META", 
                |  "_AIRBYTE_RAW_ID", 
                |  "_AIRBYTE_EXTRACTED_AT", 
                |  "_AIRBYTE_GENERATION_ID"
                |FROM 
                |numbered_rows
                |WHERE row_number = 1
                |""".trimMargin()
        } else {
            return """
            |WITH intermediate_data AS (
            |  SELECT
            |    $columnCasts
            |    ARRAY_COMPACT(
            |      ARRAY_CAT(
            |        CASE WHEN "_airbyte_meta":"changes" IS NOT NULL 
            |          THEN "_airbyte_meta":"changes" 
            |          ELSE ARRAY_CONSTRUCT()
            |        END,
            |      ARRAY_CONSTRUCT($columnErrors))) as "_airbyte_cast_errors",
            |    "_airbyte_raw_id",
            |    ${airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\"")} as "_airbyte_extracted_at",
            |    "_airbyte_meta",
            |    "_airbyte_generation_id"
            |  FROM 
            |    ${stream.id.rawTableId(QUOTE)}
            |  WHERE
            |    "_airbyte_loaded_at" IS NULL $extractedAtCondition
            |)
            |SELECT 
            |  $columnList
            |  CASE WHEN "_airbyte_meta" IS NOT NULL 
            |    THEN OBJECT_INSERT("_airbyte_meta", 'changes', "_airbyte_cast_errors", true) 
            |    ELSE OBJECT_CONSTRUCT('changes', "_airbyte_cast_errors") 
            |  END AS "_AIRBYTE_META",
            |  "_airbyte_raw_id" AS "_AIRBYTE_RAW_ID",
            |  "_airbyte_extracted_at" AS "_AIRBYTE_EXTRACTED_AT",
            |  "_airbyte_generation_id" AS "_AIRBYTE_GENERATION_ID"
            |FROM intermediate_data
            |""".trimMargin()
        }
    }

    @VisibleForTesting
    fun dedupFinalTable(
        id: StreamId,
        finalSuffix: String,
        primaryKey: List<ColumnId>,
        cursor: Optional<ColumnId>
    ): String {
        val pkList = primaryKey.joinToString { it.name(QUOTE) }
        val quotedFinalTable = id.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault()))
        val cursorOrderClause =
            cursor
                .map { cursorId: ColumnId -> "${cursorId.name(QUOTE)} DESC NULLS LAST," }
                .orElse("")
        return """
        |DELETE FROM 
        |  $quotedFinalTable
        |WHERE 
        |  "_AIRBYTE_RAW_ID" IN (
        |    SELECT "_AIRBYTE_RAW_ID" FROM (
        |      SELECT 
        |        "_AIRBYTE_RAW_ID", 
        |        row_number() OVER (PARTITION BY $pkList ORDER BY $cursorOrderClause ${airbyteExtractedAtUtcForced("\"_AIRBYTE_EXTRACTED_AT\"")} DESC) 
        |        as row_number 
        |      FROM 
        |        $quotedFinalTable
        |    )
        |    WHERE row_number != 1
        |  );
        |""".trimMargin()
    }

    private fun cdcDeletes(stream: StreamConfig, finalSuffix: String): String {
        if (stream.destinationSyncMode != DestinationSyncMode.APPEND_DEDUP) {
            return ""
        }
        if (!stream.columns.containsKey(cdcDeletedAtColumn)) {
            return ""
        }
        return """
            | DELETE FROM ${stream.id.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault()))} 
            | WHERE _AB_CDC_DELETED_AT IS NOT NULL;
        """.trimMargin()
    }

    @VisibleForTesting
    fun commitRawTable(id: StreamId): String {
        return """
            |UPDATE ${id.rawTableId(QUOTE)} 
            |SET "_airbyte_loaded_at" = CURRENT_TIMESTAMP() 
            |WHERE "_airbyte_loaded_at" IS NULL
        """.trimMargin()
    }

    override fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql {
        return transactionally(
            "DROP TABLE IF EXISTS ${stream.finalTableId(QUOTE)};",
            "ALTER TABLE ${stream.finalTableId(QUOTE, finalSuffix.uppercase(Locale.getDefault()))} RENAME TO ${stream.finalTableId(QUOTE)};"
        )
    }

    override fun prepareTablesForSoftReset(stream: StreamConfig): Sql {
        return concat(
            createTable(stream, SOFT_RESET_SUFFIX.uppercase(Locale.getDefault()), true),
            clearLoadedAt(stream.id)
        )
    }

    override fun clearLoadedAt(streamId: StreamId): Sql {
        return of("UPDATE ${streamId.rawTableId(QUOTE)} SET \"_airbyte_loaded_at\" = NULL;")
    }

    override fun migrateFromV1toV2(streamId: StreamId, namespace: String, tableName: String): Sql {
        // In the SQL below, the v2 values are quoted to preserve their case while the v1 values are
        // intentionally _not_ quoted. This is to preserve the implicit upper-casing behavior in v1.
        return of(
            """
                |CREATE OR REPLACE TABLE ${streamId.rawTableId(QUOTE)} (
                |  "${JavaBaseConstants.COLUMN_NAME_AB_RAW_ID}" VARCHAR PRIMARY KEY,
                |  "${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT}" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
                |  "${JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT}" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
                |  "${JavaBaseConstants.COLUMN_NAME_DATA}" VARIANT,
                |  "${JavaBaseConstants.COLUMN_NAME_AB_META}" VARIANT,
                |  "${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}" INTEGER
                |) 
                |data_retention_time_in_days = 0 
                |AS (
                |SELECT
                |  ${JavaBaseConstants.COLUMN_NAME_AB_ID} AS "${JavaBaseConstants.COLUMN_NAME_AB_RAW_ID}",
                |  ${JavaBaseConstants.COLUMN_NAME_EMITTED_AT} AS "${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT}",
                |  CAST(NULL AS TIMESTAMP WITH TIME ZONE) AS "${JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT}",
                |  PARSE_JSON(${JavaBaseConstants.COLUMN_NAME_DATA}) AS "${JavaBaseConstants.COLUMN_NAME_DATA}",
                |  CAST(NULL AS VARIANT) AS "${JavaBaseConstants.COLUMN_NAME_AB_META}",
                |  CAST(NULL AS INTEGER) AS "${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}",
                |  FROM $namespace.$tableName
                |);
                |""".trimMargin(),
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
            return """
                |TIMESTAMPADD(
                |  HOUR, 
                |  EXTRACT(timezone_hour from $sqlExpression), 
                |  TIMESTAMPADD(
                |    MINUTE,
                |    EXTRACT(timezone_minute from $sqlExpression),
                |    CONVERT_TIMEZONE('UTC', $sqlExpression)
                |  )
                |)
            """.trimMargin()
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
