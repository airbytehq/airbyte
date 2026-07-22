/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.redshift_v2.schema.toRedshiftCompatibleName
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.sql.ResultSet
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.util.UUID
import javax.sql.DataSource

class RedshiftDataDumper(
    private val configProvider: (ConfigurationSpecification) -> RedshiftV2Configuration,
    private val dataSourceProvider: (RedshiftV2Configuration) -> DataSource,
) : DestinationDataDumper {

    /**
     * Generate the final table name from a stream descriptor. This matches the logic in
     * RedshiftTableSchemaMapper.toFinalTableName().
     */
    private fun getTableName(
        descriptor: DestinationStream.Descriptor,
        config: RedshiftV2Configuration
    ): TableName {
        val namespace = (descriptor.namespace ?: config.schema).toRedshiftCompatibleName()
        val name = descriptor.name.toRedshiftCompatibleName()
        return TableName(namespace, name)
    }

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val dataSource = dataSourceProvider(config)

        // Get the final table name using the same logic as the connector
        val table = getTableName(stream.mappedDescriptor, config)
        val namespace = table.namespace
        val tableName = table.name

        // Build reverse mapping from sanitized column names back to original names
        // The stream.schema contains the original column names
        // Use lowercase keys since Redshift normalizes column names to lowercase
        val reverseMapping = mutableMapOf<String, String>()
        // Also build a map of original column types from the stream schema
        val originalTypeMapping = mutableMapOf<String, AirbyteType>()
        val schemaType = stream.schema
        if (schemaType is ObjectType) {
            schemaType.properties.forEach { (originalName, fieldType) ->
                val sanitizedName = originalName.toRedshiftCompatibleName().lowercase()
                reverseMapping[sanitizedName] = originalName
                originalTypeMapping[sanitizedName] = fieldType.type
            }
        }

        val output = mutableListOf<OutputRecord>()

        dataSource.connection.use { connection ->
            // First check if the table exists
            val tableExistsQuery =
                """
                SELECT COUNT(*) AS table_count
                FROM information_schema.tables
                WHERE table_schema = '$namespace'
                AND table_name = '$tableName'
            """.trimIndent()

            val existsResultSet = connection.createStatement().executeQuery(tableExistsQuery)
            existsResultSet.next()
            val tableExists = existsResultSet.getInt("table_count") > 0
            existsResultSet.close()

            if (!tableExists) {
                return output
            }

            val sql = """SELECT * FROM "$namespace"."$tableName""""
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sql)
                val metadata = rs.metaData

                while (rs.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()

                    for (i in 1..metadata.columnCount) {
                        val columnName = metadata.getColumnName(i)
                        if (!Meta.COLUMN_NAMES.contains(columnName)) {
                            // Use lowercase for lookups since Redshift normalizes column names
                            val columnNameLower = columnName.lowercase()
                            val originalColumnName = reverseMapping[columnNameLower] ?: columnName
                            val columnType = metadata.getColumnTypeName(i)
                            val originalType = originalTypeMapping[columnNameLower]
                            val value = convertResultSetValue(rs, i, columnType, originalType)
                            dataMap[originalColumnName] = value
                        }
                    }

                    val rawId =
                        rs.getString(Meta.COLUMN_NAME_AB_RAW_ID)?.let { UUID.fromString(it) }
                    val extractedAt = rs.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT).toInstant()
                    val generationId = rs.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID)
                    val metaJson = rs.getString(Meta.COLUMN_NAME_AB_META)

                    val airbyteMeta = parseAirbyteMeta(metaJson)
                    val outputRecord =
                        OutputRecord(
                            rawId = rawId,
                            extractedAt = extractedAt,
                            loadedAt = null,
                            generationId = generationId,
                            data = ObjectValue(dataMap),
                            airbyteMeta = airbyteMeta
                        )
                    output.add(outputRecord)
                }
            }
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Redshift does not support file transfer.")
    }

    private fun convertResultSetValue(
        rs: ResultSet,
        index: Int,
        columnType: String,
        originalType: AirbyteType?
    ): AirbyteValue {
        // Get raw value based on column type
        val value =
            when (columnType.lowercase()) {
                "timestamptz" -> rs.getObject(index, OffsetDateTime::class.java)
                "timestamp" -> rs.getObject(index, LocalDateTime::class.java)
                "timetz" -> rs.getObject(index, OffsetTime::class.java)
                "time" -> rs.getObject(index, LocalTime::class.java)
                "date" -> rs.getObject(index, LocalDate::class.java)
                else -> rs.getObject(index)
            }

        if (value == null) return NullValue

        // Check original Airbyte type for special handling FIRST
        // This is more reliable than checking column type since we know the original schema
        // Redshift doesn't have TIME WITH TIMEZONE, so it's stored as VARCHAR
        if (originalType == TimeTypeWithTimezone && value is String) {
            return try {
                TimeWithTimezoneValue(OffsetTime.parse(value))
            } catch (e: Exception) {
                StringValue(value)
            }
        }
        // SUPER type columns store JSON but JDBC returns as String
        // Check this BEFORE the column type check since originalType is more reliable
        if (originalType is ObjectType || originalType is UnknownType) {
            if (value is String) {
                return parseJsonValue(value)
            }
        }

        // Then check column type for SUPER (for columns not in schema, like computed columns)
        // Redshift JDBC driver may return "super" as the type name
        if (columnType.lowercase() == "super") {
            return parseJsonValue(value.toString())
        }

        // Then check value type
        return when (value) {
            is String -> StringValue(value)
            is Int -> IntegerValue(value.toLong())
            is Long -> IntegerValue(value)
            is Boolean -> BooleanValue(value)
            is BigDecimal -> NumberValue(value)
            is Double -> NumberValue(BigDecimal.valueOf(value))
            is Float -> NumberValue(BigDecimal.valueOf(value.toDouble()))
            is OffsetDateTime -> TimestampWithTimezoneValue(value)
            is LocalDateTime -> TimestampWithoutTimezoneValue(value)
            is OffsetTime -> TimeWithTimezoneValue(value)
            is LocalTime -> TimeWithoutTimezoneValue(value)
            is LocalDate -> DateValue(value)
            is java.sql.Timestamp ->
                TimestampWithTimezoneValue(value.toInstant().atOffset(java.time.ZoneOffset.UTC))
            is java.sql.Date -> DateValue(value.toLocalDate())
            is java.sql.Time -> TimeWithoutTimezoneValue(value.toLocalTime())
            else -> StringValue(value.toString())
        }
    }

    private fun parseJsonValue(json: String): AirbyteValue {
        return try {
            var node = io.airbyte.cdk.load.util.Jsons.readTree(json)
            // Redshift SUPER type may return double-encoded JSON (string containing JSON)
            // If the parsed result is a text node, try parsing its content as JSON
            // If that fails, use the text value directly (it's a plain string)
            if (node.isTextual) {
                val textContent = node.asText()
                node =
                    try {
                        io.airbyte.cdk.load.util.Jsons.readTree(textContent)
                    } catch (e: Exception) {
                        // The text content is not valid JSON, return it as a plain string
                        return StringValue(textContent)
                    }
            }
            when {
                node.isObject -> {
                    val map = linkedMapOf<String, AirbyteValue>()
                    node.fields().forEach { (key, value) -> map[key] = parseJsonNode(value) }
                    ObjectValue(map)
                }
                node.isArray -> {
                    val list = node.map { parseJsonNode(it) }
                    ArrayValue(list)
                }
                else -> parseJsonNode(node)
            }
        } catch (e: Exception) {
            StringValue(json)
        }
    }

    private fun parseJsonNode(node: com.fasterxml.jackson.databind.JsonNode): AirbyteValue {
        return when {
            node.isNull -> NullValue
            node.isTextual -> StringValue(node.asText())
            node.isIntegralNumber -> IntegerValue(node.asLong())
            node.isNumber -> NumberValue(node.decimalValue())
            node.isBoolean -> BooleanValue(node.asBoolean())
            node.isObject -> {
                val map = linkedMapOf<String, AirbyteValue>()
                node.fields().forEach { (key, value) -> map[key] = parseJsonNode(value) }
                ObjectValue(map)
            }
            node.isArray -> {
                val list = node.map { parseJsonNode(it) }
                ArrayValue(list)
            }
            else -> StringValue(node.toString())
        }
    }

    private fun parseAirbyteMeta(metaJson: String?): OutputRecord.Meta {
        if (metaJson == null) {
            return OutputRecord.Meta(syncId = null, changes = emptyList())
        }
        return try {
            // Redshift SUPER type returns JSON as a string - may need double parsing
            var node = io.airbyte.cdk.load.util.Jsons.readTree(metaJson)
            // If the result is a text node, it means the JSON was double-encoded
            if (node.isTextual) {
                node = io.airbyte.cdk.load.util.Jsons.readTree(node.asText())
            }

            val syncId = node.get("sync_id")?.asLong()
            val changes =
                node.get("changes")?.mapNotNull { change ->
                    try {
                        val field = change.get("field")?.asText() ?: return@mapNotNull null
                        val changeType =
                            change.get("change")?.asText()?.let {
                                AirbyteRecordMessageMetaChange.Change.fromValue(it)
                            }
                                ?: return@mapNotNull null
                        val reason =
                            change.get("reason")?.asText()?.let {
                                AirbyteRecordMessageMetaChange.Reason.fromValue(it)
                            }
                                ?: return@mapNotNull null
                        Meta.Change(field, changeType, reason)
                    } catch (e: Exception) {
                        null
                    }
                }
                    ?: emptyList()
            OutputRecord.Meta(syncId = syncId, changes = changes)
        } catch (e: Exception) {
            OutputRecord.Meta(syncId = null, changes = emptyList())
        }
    }
}
