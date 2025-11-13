/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.postgres.config.PostgresBeanFactory
import io.airbyte.integrations.destination.postgres.db.toPostgresCompatibleName
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.temporal.ChronoField

class PostgresRawDataDumper(
    private val configProvider: (ConfigurationSpecification) -> PostgresConfiguration
) : DestinationDataDumper {
    companion object {
        // Lenient formatters that handle PostgreSQL's JSONB serialization quirks
        // (e.g., dropping :00 seconds)
        private val TIMESTAMP_FORMATTER =
            DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd'T'HH:mm")
                .optionalStart()
                .appendPattern(":ss")
                .optionalEnd()
                .optionalStart()
                .appendPattern(".")
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, false)
                .optionalEnd()
                .appendOffsetId()
                .toFormatter()

        private val TIMESTAMP_NO_TZ_FORMATTER =
            DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd'T'HH:mm")
                .optionalStart()
                .appendPattern(":ss")
                .optionalEnd()
                .optionalStart()
                .appendPattern(".")
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, false)
                .optionalEnd()
                .toFormatter()

        private val TIME_FORMATTER =
            DateTimeFormatterBuilder()
                .appendPattern("HH:mm")
                .optionalStart()
                .appendPattern(":ss")
                .optionalEnd()
                .optionalStart()
                .appendPattern(".")
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, false)
                .optionalEnd()
                .appendOffsetId()
                .toFormatter()

        private val TIME_NO_TZ_FORMATTER =
            DateTimeFormatterBuilder()
                .appendPattern("HH:mm")
                .optionalStart()
                .appendPattern(":ss")
                .optionalEnd()
                .optionalStart()
                .appendPattern(".")
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, false)
                .optionalEnd()
                .toFormatter()

        private val DATE_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE
    }

    /**
     * Recursively coerce an AirbyteValue to match the expected schema types. This is necessary
     * because JSONB storage serializes temporal types as strings, and we need to convert them back
     * to their proper typed representations.
     */
    private fun coerceValue(value: AirbyteValue, type: AirbyteType): AirbyteValue {
        // Handle null values
        if (value is NullValue) {
            return NullValue
        }

        return when (type) {
            // For objects, recursively coerce each property
            is ObjectType -> {
                if (value !is ObjectValue) {
                    return value
                }
                val coercedProperties =
                    value.values.mapValuesTo(linkedMapOf()) { (key, propValue) ->
                        val fieldType = type.properties[key]
                        if (fieldType != null) {
                            coerceValue(propValue, fieldType.type)
                        } else {
                            propValue
                        }
                    }
                ObjectValue(coercedProperties)
            }
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema -> {
                // For objects without schema, just pass through
                value
            }
            // For arrays, recursively coerce each element
            is ArrayType -> {
                if (value !is ArrayValue) {
                    return value
                }
                val coercedElements =
                    value.values.map { elem -> coerceValue(elem, type.items.type) }
                ArrayValue(coercedElements)
            }
            is ArrayTypeWithoutSchema -> {
                // For arrays without schema, just pass through
                value
            }
            // For temporal types, use custom formatters that handle PostgreSQL's JSONB quirks
            TimestampTypeWithTimezone -> {
                if (value !is StringValue) return value
                try {
                    TimestampWithTimezoneValue(
                        OffsetDateTime.parse(value.value, TIMESTAMP_FORMATTER)
                    )
                } catch (e: Exception) {
                    // Fall back to standard coercer
                    AirbyteValueCoercer.coerce(value, type) ?: value
                }
            }
            TimestampTypeWithoutTimezone -> {
                if (value !is StringValue) return value
                try {
                    TimestampWithoutTimezoneValue(
                        LocalDateTime.parse(value.value, TIMESTAMP_NO_TZ_FORMATTER)
                    )
                } catch (e: Exception) {
                    AirbyteValueCoercer.coerce(value, type) ?: value
                }
            }
            TimeTypeWithTimezone -> {
                if (value !is StringValue) return value
                try {
                    TimeWithTimezoneValue(OffsetTime.parse(value.value, TIME_FORMATTER))
                } catch (e: Exception) {
                    AirbyteValueCoercer.coerce(value, type) ?: value
                }
            }
            TimeTypeWithoutTimezone -> {
                if (value !is StringValue) return value
                try {
                    TimeWithoutTimezoneValue(LocalTime.parse(value.value, TIME_NO_TZ_FORMATTER))
                } catch (e: Exception) {
                    AirbyteValueCoercer.coerce(value, type) ?: value
                }
            }
            DateType -> {
                if (value !is StringValue) return value
                try {
                    DateValue(LocalDate.parse(value.value, DATE_FORMATTER))
                } catch (e: Exception) {
                    AirbyteValueCoercer.coerce(value, type) ?: value
                }
            }
            // For UnknownType with PASS_THROUGH behavior, unwrap double-serialized strings
            // that were serialized during write and need to be deserialized during read
            is UnknownType -> {
                if (
                    value is StringValue &&
                        value.value.startsWith("\"") &&
                        value.value.endsWith("\"")
                ) {
                    // The value is a JSON-serialized string, unwrap it
                    try {
                        val unwrapped =
                            value.value
                                .substring(1, value.value.length - 1)
                                .replace("\\\"", "\"")
                                .replace("\\\\", "\\")
                        StringValue(unwrapped)
                    } catch (e: Exception) {
                        value
                    }
                } else {
                    value
                }
            }
            // For other primitive types, use the standard coercer
            else -> {
                val coerced = AirbyteValueCoercer.coerce(value, type)
                // If coercion returns null, it means the value couldn't be coerced to the expected
                // type.
                // In test scenarios, we want to preserve the original value to see what went wrong.
                coerced ?: value
            }
        }
    }

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val output = mutableListOf<OutputRecord>()

        val config = configProvider(spec)
        val dataSource =
            PostgresBeanFactory()
                .postgresDataSource(
                    postgresConfiguration = config,
                    resolvedHost = config.host,
                    resolvedPort = config.port
                )

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()

                // For raw tables with disable_type_dedupe, construct the raw table name
                // Raw tables follow the pattern: {namespace}_raw__stream_{name}
                val sourceNamespace = stream.unmappedDescriptor.namespace ?: config.schema
                val sourceName = stream.unmappedDescriptor.name

                // The internal schema (airbyte_internal) is used for raw tables
                // Use "airbyte_internal" as the default if internalTableSchema is not set
                val rawNamespace =
                    config.internalTableSchema?.lowercase()?.toPostgresCompatibleName()
                        ?: "airbyte_internal"

                val rawName =
                    TypingDedupingUtil.concatenateRawTableName(sourceNamespace, sourceName)
                        .lowercase()
                        .toPostgresCompatibleName()

                val fullyQualifiedTableName = "$rawNamespace.$rawName"

                // Check if table exists first
                val tableExistsQuery =
                    """
                    SELECT COUNT(*) AS table_count
                    FROM information_schema.tables
                    WHERE table_schema = '$rawNamespace'
                    AND table_name = '$rawName'
                """.trimIndent()

                val existsResultSet = statement.executeQuery(tableExistsQuery)
                existsResultSet.next()
                val tableExists = existsResultSet.getInt("table_count") > 0
                existsResultSet.close()

                if (!tableExists) {
                    // Table doesn't exist, return empty list
                    return output
                }

                val resultSet = statement.executeQuery("SELECT * FROM $fullyQualifiedTableName")

                // Check if the table has the _airbyte_data column (legacy raw table mode)
                // or individual typed columns (typed table mode)
                val hasDataColumn =
                    try {
                        resultSet.metaData.getColumnCount() > 0 &&
                            (1..resultSet.metaData.getColumnCount()).any {
                                resultSet.metaData.getColumnName(it) == Meta.COLUMN_NAME_DATA
                            }
                    } catch (e: Exception) {
                        false
                    }

                while (resultSet.next()) {
                    val rawData =
                        if (hasDataColumn) {
                            // Legacy raw table mode: read from _airbyte_data JSONB column
                            val dataObject = resultSet.getObject(Meta.COLUMN_NAME_DATA)
                            val dataJson =
                                when (dataObject) {
                                    is org.postgresql.util.PGobject -> dataObject.value
                                    else -> dataObject?.toString() ?: "{}"
                                }

                            // Parse JSON to AirbyteValue, then coerce it to match the schema
                            dataJson?.deserializeToNode()?.toAirbyteValue() ?: NullValue
                        } else {
                            // Typed table mode: read from individual columns and reconstruct the
                            // object
                            val properties = linkedMapOf<String, AirbyteValue>()

                            if (stream.schema is ObjectType) {
                                val objectSchema = stream.schema as ObjectType

                                // Build a map of lowercase column names to actual column names from
                                // the result set
                                val columnMap = mutableMapOf<String, String>()
                                for (i in 1..resultSet.metaData.getColumnCount()) {
                                    val actualColumnName = resultSet.metaData.getColumnName(i)
                                    columnMap[actualColumnName.lowercase()] = actualColumnName
                                }

                                for ((fieldName, fieldType) in objectSchema.properties) {
                                    try {
                                        // Try to find the actual column name (case-insensitive
                                        // lookup)
                                        val actualColumnName =
                                            columnMap[fieldName.lowercase()] ?: fieldName
                                        val columnValue = resultSet.getObject(actualColumnName)
                                        properties[fieldName] =
                                            when (columnValue) {
                                                null -> NullValue
                                                is org.postgresql.util.PGobject -> {
                                                    // JSONB columns (for arrays, objects, unknown
                                                    // types)
                                                    columnValue.value
                                                        ?.deserializeToNode()
                                                        ?.toAirbyteValue()
                                                        ?: NullValue
                                                }
                                                else -> {
                                                    // Primitive types - convert directly
                                                    when (fieldType.type) {
                                                        is io.airbyte.cdk.load.data.IntegerType ->
                                                            io.airbyte.cdk.load.data.IntegerValue(
                                                                (columnValue as Number).toLong()
                                                            )
                                                        is io.airbyte.cdk.load.data.NumberType ->
                                                            io.airbyte.cdk.load.data.NumberValue(
                                                                (columnValue
                                                                        as java.math.BigDecimal)
                                                                    .toDouble()
                                                                    .toBigDecimal()
                                                            )
                                                        is io.airbyte.cdk.load.data.BooleanType ->
                                                            io.airbyte.cdk.load.data.BooleanValue(
                                                                columnValue as Boolean
                                                            )
                                                        is io.airbyte.cdk.load.data.StringType ->
                                                            StringValue(columnValue.toString())
                                                        else -> StringValue(columnValue.toString())
                                                    }
                                                }
                                            }
                                    } catch (e: Exception) {
                                        // Column doesn't exist or error reading it, set to null
                                        properties[fieldName] = NullValue
                                    }
                                }
                            }

                            ObjectValue(properties)
                        }

                    val coercedData = coerceValue(rawData, stream.schema)

                    val outputRecord =
                        OutputRecord(
                            rawId = resultSet.getString(Meta.COLUMN_NAME_AB_RAW_ID),
                            extractedAt =
                                resultSet
                                    .getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
                                    .toInstant()
                                    .toEpochMilli(),
                            loadedAt = null,
                            generationId = resultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID),
                            data = coercedData,
                            airbyteMeta =
                                stringToMeta(resultSet.getString(Meta.COLUMN_NAME_AB_META))
                        )
                    output.add(outputRecord)
                }
                resultSet.close()
            }
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Postgres does not support file transfer.")
    }
}
