/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Change
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.sql.ResultSet
import java.time.Instant
import java.util.*

/**
 * Reads typed final tables from Databricks and converts rows to [OutputRecord] for test
 * verification. Handles Databricks-specific type conversions.
 */
class DatabricksDataDumper(
    private val configProvider: (ConfigurationSpecification) -> DatabricksV2Configuration,
) : DestinationDataDumper {

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val dataSource = DatabricksTestDataSourceProvider.get(config)
        val tableName = stream.tableSchema.tableNames.finalTableName!!

        // Build reverse column name mapping (final -> input)
        val columnMapping = stream.tableSchema.columnSchema.inputToFinalColumnNames
        val reverseMapping = columnMapping.entries.associate { (k, v) -> v to k }

        val sql = "SELECT * FROM `${config.database}`.`${tableName.namespace}`.`${tableName.name}`"

        return dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs ->
                    val meta = rs.metaData
                    val records = mutableListOf<OutputRecord>()
                    while (rs.next()) {
                        val rawId =
                            rs.getString(Meta.COLUMN_NAME_AB_RAW_ID)?.let { UUID.fromString(it) }
                        val extractedAt =
                            rs.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT)?.toInstant()
                                ?: Instant.EPOCH
                        val generationId =
                            rs.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID).let {
                                if (rs.wasNull()) null else it
                            }
                        val airbyteMeta = parseAirbyteMeta(rs.getString(Meta.COLUMN_NAME_AB_META))

                        // Read user columns
                        val data = linkedMapOf<String, Any?>()
                        for (i in 1..meta.columnCount) {
                            val colName = meta.getColumnName(i)
                            if (colName in Meta.COLUMN_NAMES) continue

                            val originalName = reverseMapping[colName] ?: colName
                            data[originalName] = readColumnValue(rs, i, meta.getColumnTypeName(i))
                        }

                        records.add(
                            OutputRecord(
                                rawId = rawId,
                                extractedAt = extractedAt,
                                loadedAt = null,
                                generationId = generationId,
                                data = ObjectValue.from(data),
                                airbyteMeta = airbyteMeta,
                            ),
                        )
                    }
                    records
                }
            }
        }
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): Map<String, String> {
        throw UnsupportedOperationException("Databricks does not support file transfer")
    }

    companion object {
        private fun readColumnValue(rs: ResultSet, index: Int, typeName: String): Any? {
            val value = rs.getObject(index) ?: return null
            return when (typeName.uppercase()) {
                "TIMESTAMP",
                "TIMESTAMP_NTZ" -> rs.getTimestamp(index)?.toLocalDateTime()?.toString()
                "DATE" -> rs.getDate(index)?.toString()
                "LONG",
                "BIGINT",
                "INT" -> rs.getLong(index)
                "DECIMAL" -> rs.getBigDecimal(index) ?: BigDecimal.ZERO
                "BOOLEAN" -> rs.getBoolean(index)
                "STRING" -> {
                    val str = rs.getString(index)
                    // Try to parse as JSON for structured types
                    tryParseJson(str) ?: str
                }
                else -> rs.getObject(index)
            }
        }

        private fun tryParseJson(str: String): Any? {
            if (str.isBlank()) return str
            val trimmed = str.trim()
            if (!trimmed.startsWith("{") && !trimmed.startsWith("[")) return null
            return try {
                Jsons.readValue(trimmed, Any::class.java)
            } catch (_: Exception) {
                null
            }
        }

        fun parseAirbyteMeta(metaStr: String?): OutputRecord.Meta? {
            if (metaStr.isNullOrBlank()) return null
            return try {
                val node = Jsons.readTree(metaStr)
                val changes =
                    node.get("changes")?.map { change ->
                        Change(
                            field = change.get("field")?.asText() ?: "",
                            change =
                                AirbyteRecordMessageMetaChange.Change.valueOf(
                                    change.get("change")?.asText() ?: "NULLED",
                                ),
                            reason =
                                AirbyteRecordMessageMetaChange.Reason.valueOf(
                                    change.get("reason")?.asText()
                                        ?: "DESTINATION_SERIALIZATION_ERROR",
                                ),
                        )
                    }
                        ?: emptyList()
                val syncId = node.get("sync_id")?.asLong()
                OutputRecord.Meta(changes = changes, syncId = syncId)
            } catch (_: Exception) {
                null
            }
        }
    }
}
