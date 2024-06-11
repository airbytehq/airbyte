/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.jdbc

import io.airbyte.cdk.integrations.base.JavaBaseConstants as constants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange.*
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.*

class DatabricksSqlGenerator(
    private val namingTransformer: NamingConventionTransformer,
    private val unityCatalogName: String,
) : SqlGenerator {

    private val log = KotlinLogging.logger {}
    private val cdcDeletedColumn = buildColumnId(CDC_DELETED_COLUMN_NAME)
    private val metaColumnTypeMap =
        mapOf(
            buildColumnId(AB_RAW_ID) to AirbyteProtocolType.STRING,
            buildColumnId(AB_EXTRACTED_AT) to AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE,
            buildColumnId(AB_META) to AirbyteProtocolType.STRING
        )

    companion object {
        const val QUOTE = "`"
        const val CDC_DELETED_COLUMN_NAME = "_ab_cdc_deleted_at"
        const val AB_RAW_ID = constants.COLUMN_NAME_AB_RAW_ID
        const val AB_EXTRACTED_AT = constants.COLUMN_NAME_AB_EXTRACTED_AT
        const val AB_LOADED_AT = constants.COLUMN_NAME_AB_LOADED_AT
        const val AB_DATA = constants.COLUMN_NAME_DATA
        const val AB_META = constants.COLUMN_NAME_AB_META

        fun toDialectType(type: AirbyteType): String {
            return when (type) {
                is AirbyteProtocolType -> toDialectType(type)

                // Databricks has only STRING for semi structured data, else we need to map
                // each subTypes inside the Struct and Array
                is Struct,
                is Array,
                is UnsupportedOneOf -> "STRING"
                is Union -> toDialectType(type.chooseType())
                else -> {
                    throw IllegalArgumentException("Unsupported AirbyteType $type")
                }
            }
        }

        private fun toDialectType(type: AirbyteProtocolType): String {
            return when (type) {
                AirbyteProtocolType.STRING,
                AirbyteProtocolType.TIME_WITHOUT_TIMEZONE,
                AirbyteProtocolType.TIME_WITH_TIMEZONE,
                AirbyteProtocolType.UNKNOWN -> "STRING"
                AirbyteProtocolType.DATE -> "DATE"
                AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> "TIMESTAMP_NTZ"
                AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> "TIMESTAMP"
                AirbyteProtocolType.NUMBER -> "DECIMAL(38, 10)"
                AirbyteProtocolType.INTEGER -> "LONG"
                AirbyteProtocolType.BOOLEAN -> "BOOLEAN"
            }
        }
    }
    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        return StreamId(
            namingTransformer.getNamespace(namespace),
            namingTransformer.getIdentifier(name),
            namingTransformer.getNamespace(rawNamespaceOverride),
            namingTransformer.getIdentifier(StreamId.concatenateRawTableName(namespace, name)),
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

    // Start: Functions scattered over other classes needed for T+D
    fun createRawTable(streamId: StreamId): Sql {
        return Sql.of(
            """
                CREATE TABLE IF NOT EXISTS $unityCatalogName.${streamId.rawNamespace}.${streamId.rawName} (
                    $AB_RAW_ID STRING,
                    $AB_EXTRACTED_AT TIMESTAMP,
                    $AB_LOADED_AT TIMESTAMP,
                    $AB_DATA STRING,
                    $AB_META STRING
                )
            """.trimIndent(),
        )
    }

    fun truncateRawTable(streamId: StreamId): Sql {
        return Sql.of(
            "TRUNCATE TABLE $unityCatalogName.${streamId.rawNamespace}.${streamId.rawName}"
        )
    }

    private fun checkpointRawTable(streamId: StreamId, minRawTimestamp: Optional<Instant>): Sql {
        val extractedAtCondition =
            minRawTimestamp.map { " AND `$AB_EXTRACTED_AT` > '$it'" }.orElse("")

        return Sql.of(
            """
            | UPDATE $unityCatalogName.${streamId.rawTableId(QUOTE)}
            | SET ${constants.COLUMN_NAME_AB_LOADED_AT} = CURRENT_TIMESTAMP
            | WHERE ${constants.COLUMN_NAME_AB_LOADED_AT} IS NULL
            | $extractedAtCondition
            | """.trimMargin()
        )
    }

    // End: Functions

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        val columnNameTypeMapping =
            sequenceOf(metaColumnTypeMap.asSequence(), stream.columns.asSequence())
                .flatten()
                .map { it -> "${it.key.name(QUOTE)} ${toDialectType(it.value)}" }
                .toList()
                .joinToString(", \n")
        val finalTableIdentifier = stream.id.finalName + namingTransformer.applyDefaultCase(suffix)
        return Sql.of(
            """
            CREATE ${if (force) "OR REPLACE" else ""} TABLE $unityCatalogName.`${stream.id.finalNamespace}`.`$finalTableIdentifier`(
                $columnNameTypeMapping
            )
        """.trimIndent(),
        )
    }

    override fun createSchema(schema: String): Sql {
        return Sql.of("CREATE SCHEMA IF NOT EXISTS $unityCatalogName.`$schema`")
    }

    override fun updateTable(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql {

        val addRecordsToFinalTable =
            if (stream.destinationSyncMode == DestinationSyncMode.APPEND_DEDUP) {
                upsertNewRecords(stream, finalSuffix, minRawTimestamp, useExpensiveSaferCasting)
            } else {
                insertNewRecordsNoDedupe(
                    stream,
                    finalSuffix,
                    minRawTimestamp,
                    useExpensiveSaferCasting,
                )
            }

        return Sql.concat(addRecordsToFinalTable, checkpointRawTable(stream.id, minRawTimestamp))
    }

    private fun upsertNewRecords(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        safeCast: Boolean
    ): Sql {
        val finalColumnNames =
            sequenceOf(
                    stream.columns.keys.asSequence(),
                    metaColumnTypeMap.keys.filter { it.name != AB_META }.asSequence(),
                )
                .flatten()
                .joinToString(", \n") { it.name(QUOTE) }

        val pkEqualityMatch =
            stream.primaryKey
                .map { it.name(QUOTE) }
                .joinToString(
                    separator = " AND \n",
                    transform = {
                        """
                    | (target_table.$it=deduped_records.$it OR (target_table.$it IS NULL AND deduped_records.$it IS NULL))
                """.trimMargin()
                    }
                )

        val cursorCompareCondition =
            stream.cursor
                .map { it.name(QUOTE) }
                .map {
                    """
                | (target_table.$it < deduped_records.$it
                | OR (target_table.$it = deduped_records.$it AND target_table.$AB_EXTRACTED_AT < deduped_records.$AB_EXTRACTED_AT)
                | OR (target_table.$it IS NULL AND deduped_records.$it IS NULL AND target_table.$AB_EXTRACTED_AT < deduped_records.$AB_EXTRACTED_AT)
                | OR (target_table.$it IS NULL AND deduped_records.$it IS NOT NULL))
            """.trimMargin()
                }
                .orElse("target_table.$AB_EXTRACTED_AT < deduped_records.$AB_EXTRACTED_AT")

        val whenMatchedCdcDeleteCondition =
            if (stream.columns.containsKey(cdcDeletedColumn))
                "WHEN MATCHED AND deduped_records.$CDC_DELETED_COLUMN_NAME IS NOT NULL AND $cursorCompareCondition THEN DELETE"
            else ""
        val whenNotMatchedCdcSkipCondition =
            if (stream.columns.containsKey(cdcDeletedColumn))
                "AND deduped_records.$CDC_DELETED_COLUMN_NAME IS NULL"
            else ""

        val upsertSql =
            """
            |MERGE INTO $unityCatalogName.${stream.id.finalTableId(QUOTE, finalSuffix)} as target_table
            |USING (
            |${selectTypedRecordsFromRawTable(stream, minRawTimestamp, finalColumnNames, safeCast, true).replaceIndent("   ")}
            |) deduped_records
            |ON 
            |${pkEqualityMatch.replaceIndent("   ")}
            |$whenMatchedCdcDeleteCondition
            |WHEN MATCHED AND $cursorCompareCondition THEN UPDATE SET *
            |WHEN NOT MATCHED $whenNotMatchedCdcSkipCondition THEN INSERT * 
        """.trimMargin()
        return Sql.of(upsertSql)
    }

    private fun insertNewRecordsNoDedupe(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        safeCast: Boolean
    ): Sql {

        val finalColumnNames =
            sequenceOf(
                    stream.columns.keys.asSequence(),
                    metaColumnTypeMap.keys.filter { it.name != AB_META }.asSequence(),
                )
                .flatten()
                .joinToString(", \n") { it.name(QUOTE) }

        val insertSql =
            """INSERT INTO $unityCatalogName.${stream.id.finalTableId(QUOTE, finalSuffix)}
                           |(
                           |${finalColumnNames.replaceIndent("    ")},
                           |    $AB_META
                           |)
                           |${selectTypedRecordsFromRawTable(stream, minRawTimestamp, finalColumnNames, safeCast, false)}""".trimMargin()

        return Sql.of(insertSql)
    }

    private fun cast(columnName: String, columnType: AirbyteType, safeCast: Boolean): String {
        if (!safeCast) {
            return "${jsonPath(columnName)}::${toDialectType(columnType)}"
        }
        return "try_cast(${jsonPath(columnName)} AS ${toDialectType(columnType)})"
    }

    private fun jsonPath(originalColumnName: String): String {
        // get_json_object seems safer to do which doesn't crash on special chars in json
        return "get_json_object(`$AB_DATA`, '$[\"${
            originalColumnName.replace("\\", "\\\\").replace("'", "\\'")
        }\"]')"
        // return "`$AB_DATA`:`${originalColumnName.replace("`", "``")}`"
    }

    private fun selectTypedRecordsFromRawTable(
        stream: StreamConfig,
        minRawTimestamp: Optional<Instant>,
        finalColumnNames: String,
        safeCast: Boolean,
        dedupe: Boolean
    ): String {

        // JsonPath queried projection columns from raw Table.
        val projectionColumns =
            sequenceOf(
                    stream.columns.entries.asSequence().map {
                        "${cast(it.key.originalName, it.value, safeCast)} as `${it.key.name}`"
                    },
                    metaColumnTypeMap
                        .asSequence()
                        .filter { it.key.name != AB_META }
                        .map { it.key.name },
                )
                .flatten()
                .joinToString(", \n")

        // Condition to avoid resurrecting phantom data from out of order deletes/updates
        val excludeCdcDeletedCondition =
            if (
                dedupe &&
                    stream.columns.containsKey(
                        cdcDeletedColumn,
                    )
            )
                " OR ($AB_LOADED_AT IS NOT NULL AND `$AB_DATA`:`$CDC_DELETED_COLUMN_NAME` IS NOT NULL)"
            else ""

        val extractedAtCondition =
            minRawTimestamp.map { " AND `$AB_EXTRACTED_AT` > '$it'" }.orElse("")

        // Selection clause for raw table extraction
        val rawTableSelectionCondition =
            """
            ($AB_LOADED_AT is NULL$excludeCdcDeletedCondition)$extractedAtCondition
        """.trimIndent()

        // Airbyte meta - casting errors struct
        val typeCastErrors =
            stream.columns.entries.joinToString(
                separator = ", \n",
                transform = {
                    """
                    |CASE
                    |   WHEN ${jsonPath(it.key.originalName)} IS NOT NULL
                    |   AND ${cast(it.key.originalName, it.value, false)} IS NULL THEN named_struct(
                    |       'field',
                    |       '${it.key.name}',
                    |       'change',
                    |       '${Change.NULLED.value()}',
                    |       'reason',
                    |       '${Reason.DESTINATION_TYPECAST_ERROR}'
                    |   )
                    |   ELSE NULL
                    |END
                    """.trimMargin()
                },
            )
        val typeCastErrorsArray =
            """
            |array_compact(
            |   array(
            |${typeCastErrors.replaceIndent("       ")}
            |   )
            |)
            """.trimMargin()
        val airbyteMetaField =
            """
            |to_json(
            |   named_struct(
            |       "changes",
            |       array_union(
            |           _airbyte_type_errors,
            |           CASE
            |               WHEN _airbyte_meta.changes IS NULL THEN ARRAY()
            |               ELSE _airbyte_meta.changes
            |           END
            |       )
            |   )
            |)
            """.trimMargin()
        val selectFromRawTable =
            """SELECT
            |${projectionColumns.replaceIndent("   ")},
            |   from_json($AB_META, 'STRUCT<`changes` : ARRAY<STRUCT<`field`: STRING, `change`: STRING, `reason`: STRING>>>') as `_airbyte_meta`,
            |${typeCastErrorsArray.replaceIndent("   ")} as `_airbyte_type_errors`
            |FROM
            |   $unityCatalogName.${stream.id.rawTableId(QUOTE)}
            |WHERE
            |   $rawTableSelectionCondition""".trimMargin()

        val selectCTENoDedupe =
            """WITH intermediate_data as (
            |${selectFromRawTable.replaceIndent("     ")}
            |)
            |SELECT 
            |${finalColumnNames.replaceIndent("     ")},
            |${airbyteMetaField.replaceIndent("     ")} as $AB_META
            |FROM
            |     intermediate_data""".trimMargin()
        if (!dedupe) {
            return selectCTENoDedupe
        }

        val cursorOrderBy = stream.cursor.map { "${it.name(QUOTE)} DESC NULLS LAST," }.orElse("")
        val commaSeperatedPks = stream.primaryKey.joinToString { it.name(QUOTE) }

        val selectCTEDedupe =
            """
            |WITH intermediate_data as (
            |${selectFromRawTable.replaceIndent("       ")}
            |), new_records AS (
            |   SELECT
            |${finalColumnNames.replaceIndent("       ")},
            |${airbyteMetaField.replaceIndent("       ")} as $AB_META
            |   FROM
            |       intermediate_data
            |), numbered_rows AS (
            |   SELECT *, row_number() OVER (
            |       PARTITION BY $commaSeperatedPks ORDER BY $cursorOrderBy `$AB_EXTRACTED_AT` DESC
            |   ) as row_number
            |   FROM
            |       new_records
            |)
            |SELECT
            |${finalColumnNames.replaceIndent("   ")},
            |   $AB_META
            |FROM
            |   numbered_rows
            |WHERE
            |   row_number=1
        """.trimMargin()

        return selectCTEDedupe
    }

    override fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql {
        // CREATE OR REPLACE atomically swaps temp to actual table.
        // DROP the temp table later
        return Sql.concat(
            Sql.of(
                """
                CREATE OR REPLACE TABLE $unityCatalogName.${stream.finalTableId(QUOTE)}
                AS SELECT * FROM $unityCatalogName.${stream.finalTableId(QUOTE, finalSuffix)}
            """.trimIndent(),
            ),
            Sql.of("DROP TABLE $unityCatalogName.${stream.finalTableId(QUOTE, finalSuffix)}"),
        )
    }

    override fun migrateFromV1toV2(streamId: StreamId, namespace: String, tableName: String): Sql {
        throw UnsupportedOperationException(
            "This method is not allowed in Databricks and should not be called"
        )
    }

    override fun clearLoadedAt(streamId: StreamId): Sql {
        return Sql.of(
            """
            UPDATE $unityCatalogName.${streamId.rawTableId(QUOTE)}
            SET $AB_LOADED_AT = NULL
        """.trimIndent(),
        )
    }
}
