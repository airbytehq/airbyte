/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import java.math.BigDecimal
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException
import java.util.*
import microsoft.sql.DateTimeOffset
import org.apache.kafka.connect.data.SchemaBuilder
import org.slf4j.LoggerFactory

class MsSqlServerDebeziumConverter : CustomConverter<SchemaBuilder, RelationalColumn> {

    companion object {
        private val logger = LoggerFactory.getLogger(MsSqlServerDebeziumConverter::class.java)
        private const val MSSQL_DATE_TYPE = "DATE"
        private const val MSSQL_DATETIME_TYPE = "DATETIME"
        private const val MSSQL_DATETIME2_TYPE = "DATETIME2"
        private const val MSSQL_SMALLDATETIME_TYPE = "SMALLDATETIME"
        private const val MSSQL_DATETIMEOFFSET_TYPE = "DATETIMEOFFSET"
        private const val MSSQL_TIME_TYPE = "TIME"
        private const val MSSQL_SMALLMONEY_TYPE = "SMALLMONEY"
        private const val MSSQL_MONEY_TYPE = "MONEY"
        private const val MSSQL_BINARY_TYPE = "BINARY"
        private const val MSSQL_VARBINARY_TYPE = "VARBINARY"
        private const val MSSQL_IMAGE_TYPE = "IMAGE"
        private const val MSSQL_GEOMETRY_TYPE = "GEOMETRY"
        private const val MSSQL_GEOGRAPHY_TYPE = "GEOGRAPHY"
        private const val MSSQL_UNIQUEIDENTIFIER_TYPE = "UNIQUEIDENTIFIER"
        private const val MSSQL_XML_TYPE = "XML"
        private const val MSSQL_HIERARCHYID_TYPE = "HIERARCHYID"
        private const val MSSQL_SQL_VARIANT_TYPE = "SQL_VARIANT"
    }

    override fun configure(properties: Properties) {
        // No configuration needed
    }

    override fun converterFor(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        val typeName = field.typeName().uppercase()

        when (typeName) {
            MSSQL_DATE_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertDate)
            }
            MSSQL_DATETIME_TYPE,
            MSSQL_DATETIME2_TYPE,
            MSSQL_SMALLDATETIME_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertDateTime)
            }
            MSSQL_DATETIMEOFFSET_TYPE -> {
                registration.register(
                    SchemaBuilder.string().optional(),
                    this::convertDateTimeOffset
                )
            }
            MSSQL_TIME_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertTime)
            }
            MSSQL_SMALLMONEY_TYPE,
            MSSQL_MONEY_TYPE -> {
                registration.register(SchemaBuilder.float64().optional(), this::convertMoney)
            }
            MSSQL_BINARY_TYPE,
            MSSQL_VARBINARY_TYPE,
            MSSQL_IMAGE_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertBinary)
            }
            MSSQL_GEOMETRY_TYPE,
            MSSQL_GEOGRAPHY_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertSpatial)
            }
            MSSQL_UNIQUEIDENTIFIER_TYPE -> {
                registration.register(
                    SchemaBuilder.string().optional(),
                    this::convertUniqueIdentifier
                )
            }
            MSSQL_XML_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertXml)
            }
            MSSQL_HIERARCHYID_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertHierarchyId)
            }
            MSSQL_SQL_VARIANT_TYPE -> {
                registration.register(SchemaBuilder.string().optional(), this::convertSqlVariant)
            }
            else -> {
                // For unhandled types, just return as string
                logger.debug("Unhandled SQL Server type: {}", typeName)
            }
        }
    }

    private fun convertDate(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is LocalDate -> value.toString()
                is String -> {
                    // Try to parse and reformat to ensure consistent format
                    val date = LocalDate.parse(value, DateTimeFormatter.ISO_LOCAL_DATE)
                    date.toString()
                }
                is java.sql.Date -> value.toLocalDate().toString()
                else -> value.toString()
            }
        } catch (e: DateTimeParseException) {
            logger.warn("Failed to parse date value: {}", value, e)
            value.toString()
        }
    }

    private fun convertDateTime(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is LocalDateTime -> value.atZone(ZoneOffset.UTC).toInstant().toString()
                is String -> {
                    // Try to parse as LocalDateTime first
                    val dateTime = LocalDateTime.parse(value.replace(" ", "T"))
                    dateTime.atZone(ZoneOffset.UTC).toInstant().toString()
                }
                is java.sql.Timestamp -> value.toInstant().toString()
                is Instant -> value.toString()
                else -> value.toString()
            }
        } catch (e: DateTimeParseException) {
            logger.warn("Failed to parse datetime value: {}", value, e)
            value.toString()
        }
    }

    private fun convertDateTimeOffset(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is DateTimeOffset -> value.offsetDateTime.toString()
                is OffsetDateTime -> value.toString()
                is String -> {
                    // Try to parse as OffsetDateTime
                    val offsetDateTime = OffsetDateTime.parse(value)
                    offsetDateTime.toString()
                }
                else -> value.toString()
            }
        } catch (e: Exception) {
            logger.warn("Failed to parse datetimeoffset value: {}", value, e)
            value.toString()
        }
    }

    private fun convertTime(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is LocalTime -> value.toString()
                is String -> {
                    val time = LocalTime.parse(value)
                    time.toString()
                }
                is java.sql.Time -> value.toLocalTime().toString()
                else -> value.toString()
            }
        } catch (e: Exception) {
            logger.warn("Failed to parse time value: {}", value, e)
            value.toString()
        }
    }

    private fun convertMoney(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is BigDecimal -> value.toDouble()
                is Double -> value
                is String -> value.toBigDecimal().toDouble()
                is Number -> value.toDouble()
                else -> value.toString().toBigDecimal().toDouble()
            }
        } catch (e: Exception) {
            logger.warn("Failed to parse money value: {}", value, e)
            null
        }
    }

    private fun convertBinary(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is ByteArray -> Base64.getEncoder().encodeToString(value)
                is String -> value // Already encoded
                else -> {
                    logger.warn("Unexpected binary type: {}", value.javaClass.name)
                    value.toString()
                }
            }
        } catch (e: Exception) {
            logger.warn("Failed to convert binary value: {}", value, e)
            value.toString()
        }
    }

    private fun convertSpatial(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is String -> value
                is ByteArray -> {
                    // Try to convert spatial binary to WKT format
                    try {
                        // This is a simplified conversion - in production you might want
                        // to use a proper spatial library like JTS
                        Base64.getEncoder().encodeToString(value)
                    } catch (e: Exception) {
                        logger.warn("Failed to convert spatial binary to WKT: {}", e.message)
                        Base64.getEncoder().encodeToString(value)
                    }
                }
                else -> value.toString()
            }
        } catch (e: Exception) {
            logger.warn("Failed to convert spatial value: {}", value, e)
            value.toString()
        }
    }

    private fun convertUniqueIdentifier(value: Any?): Any? {
        if (value == null) return null

        return try {
            when (value) {
                is UUID -> value.toString()
                is String -> {
                    // Validate UUID format
                    UUID.fromString(value).toString()
                }
                else -> value.toString()
            }
        } catch (e: Exception) {
            logger.warn("Failed to convert UUID value: {}", value, e)
            value.toString()
        }
    }

    private fun convertXml(value: Any?): Any? {
        if (value == null) return null

        return try {
            // XML is stored as string in Airbyte
            value.toString()
        } catch (e: Exception) {
            logger.warn("Failed to convert XML value: {}", value, e)
            value.toString()
        }
    }

    private fun convertHierarchyId(value: Any?): Any? {
        if (value == null) return null

        return try {
            // HierarchyID is stored as string representation
            value.toString()
        } catch (e: Exception) {
            logger.warn("Failed to convert HierarchyID value: {}", value, e)
            value.toString()
        }
    }

    private fun convertSqlVariant(value: Any?): Any? {
        if (value == null) return null

        return try {
            // SQL_VARIANT can hold various types - store as string
            value.toString()
        } catch (e: Exception) {
            logger.warn("Failed to convert SQL_VARIANT value: {}", value, e)
            value.toString()
        }
    }
}
