/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Change
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.databricksv2.schema.DatabricksTableSchemaMapper
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.airbyte.integrations.destination.databricksv2.sql.DatabricksSqlGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.sql.ResultSet
import java.time.Instant
import java.time.ZoneOffset
import java.util.Calendar
import java.util.TimeZone
import java.util.UUID

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

        val schemaMapper = DatabricksTableSchemaMapper(config, DefaultTempTableNameGenerator())
        val sqlGenerator = DatabricksSqlGenerator(config)
        val tableName = schemaMapper.toFinalTableName(stream.mappedDescriptor)

        // Return empty list if the table doesn't exist (e.g., incomplete truncate sync
        // where the real table was never created). Mirrors RedshiftDataDumper pattern.
        val tableExists =
            dataSource.connection.use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.executeQuery(sqlGenerator.tableExists(tableName)).use { rs ->
                        rs.next() && rs.getBoolean("table_exists")
                    }
                }
            }
        if (!tableExists) return emptyList()

        val sql = "SELECT * FROM ${sqlGenerator.fullyQualifiedName(tableName)}"

        // Reverse column name mapping: sanitized Databricks name -> original input name.
        val reverseMapping =
            stream.tableSchema.columnSchema.inputSchema.keys.associate {
                schemaMapper.toColumnName(it) to it
            }

        // Columns with Object/Array types -- only these STRING columns get JSON parsing.
        val jsonColumns =
            stream.tableSchema.columnSchema.inputSchema
                .filterValues {
                    it.type is ObjectType ||
                        it.type is ObjectTypeWithoutSchema ||
                        it.type is ObjectTypeWithEmptySchema ||
                        it.type is ArrayType ||
                        it.type is ArrayTypeWithoutSchema
                }
                .keys
                .mapTo(mutableSetOf()) { schemaMapper.toColumnName(it) }

        return dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs ->
                    val meta = rs.metaData
                    buildList {
                        while (rs.next()) {
                            val rawId =
                                rs.getString(Meta.COLUMN_NAME_AB_RAW_ID)?.let {
                                    UUID.fromString(it)
                                }
                            val extractedAt =
                                rs.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT, utcCalendar())
                                    ?.toInstant()
                                    ?: Instant.EPOCH
                            val generationId =
                                rs.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID).let {
                                    if (rs.wasNull()) null else it
                                }
                            val airbyteMeta =
                                parseAirbyteMeta(rs.getString(Meta.COLUMN_NAME_AB_META))

                            val data = linkedMapOf<String, Any?>()
                            for (i in 1..meta.columnCount) {
                                val colName = meta.getColumnName(i)
                                if (colName in Meta.COLUMN_NAMES) continue

                                val originalName = reverseMapping[colName] ?: colName
                                data[originalName] =
                                    readColumnValue(
                                        rs,
                                        i,
                                        meta.getColumnTypeName(i),
                                        colName in jsonColumns,
                                    )
                            }

                            add(
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
                    }
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
        private fun utcCalendar(): Calendar = Calendar.getInstance(TimeZone.getTimeZone("UTC"))

        private fun readColumnValue(
            rs: ResultSet,
            index: Int,
            typeName: String,
            isJsonColumn: Boolean,
        ): Any? {
            rs.getObject(index) ?: return null
            return when (typeName.uppercase()) {
                "TIMESTAMP" ->
                    rs.getTimestamp(index, utcCalendar())?.toInstant()?.atOffset(ZoneOffset.UTC)
                "TIMESTAMP_NTZ" -> rs.getTimestamp(index, utcCalendar())?.toLocalDateTime()
                "DATE" -> rs.getDate(index)?.toLocalDate()
                "LONG",
                "BIGINT",
                "INT" -> rs.getLong(index)
                "DECIMAL" -> rs.getBigDecimal(index) ?: BigDecimal.ZERO
                "BOOLEAN" -> rs.getBoolean(index)
                "STRING" -> {
                    val str = rs.getString(index)
                    // Only parse JSON for Object/Array columns, not stringified unions.
                    if (isJsonColumn) tryParseJson(str) ?: str else str
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
