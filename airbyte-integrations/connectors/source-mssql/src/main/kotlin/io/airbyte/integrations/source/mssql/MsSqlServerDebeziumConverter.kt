package io.airbyte.integrations.source.mssql

import com.microsoft.sqlserver.jdbc.Geography
import com.microsoft.sqlserver.jdbc.Geometry
import com.microsoft.sqlserver.jdbc.SQLServerException
import io.airbyte.cdk.jdbc.converters.DataTypeUtils
import io.airbyte.cdk.jdbc.converters.DateTimeConverter
import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.github.oshai.kotlinlogging.KotlinLogging
import microsoft.sql.DateTimeOffset
import org.apache.kafka.connect.data.SchemaBuilder
import java.math.BigDecimal
import java.sql.Timestamp
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.*

class MsSqlServerDebeziumConverter: CustomConverter<SchemaBuilder, RelationalColumn> {
    override fun configure(props: Properties?) {}

    override fun converterFor(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        if (DATE.equals(field.typeName(), ignoreCase = true)) {
            registerDate(field, registration)
        } else if (DATETIME_TYPES.contains(field.typeName().uppercase(Locale.getDefault()))) {
            registerDatetime(field, registration)
        } else if (SMALLMONEY_TYPE.equals(field.typeName(), ignoreCase = true)) {
            registerMoney(field, registration)
        } else if (BINARY.contains(field.typeName().uppercase(Locale.getDefault()))) {
            registerBinary(field, registration)
        } else if (GEOMETRY.equals(field.typeName(), ignoreCase = true)) {
            registerGeometry(field, registration)
        } else if (GEOGRAPHY.equals(field.typeName(), ignoreCase = true)) {
            registerGeography(field, registration)
        } else if (TIME_TYPE.equals(field.typeName(), ignoreCase = true)) {
            registerTime(field, registration)
        } else if (DATETIMEOFFSET.equals(field.typeName(), ignoreCase = true)) {
            registerDateTimeOffSet(field, registration)
        }
    }

    private fun registerGeometry(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.string()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (input is ByteArray) {
                try {
                    return@register Geometry.deserialize(input).toString()
                } catch (e: SQLServerException) {
                    LOGGER.error{e.message}
                }
            }

            LOGGER.warn {
                "Uncovered Geometry class type '${input.javaClass.name}'. Use default converter"
            }
            input.toString()
        }
    }

    private fun registerGeography(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.string()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (input is ByteArray) {
                try {
                    return@register Geography.deserialize(input).toString()
                } catch (e: SQLServerException) {
                    LOGGER.error{e.message}
                }
            }

            LOGGER.warn {
                "Uncovered Geography class type '${input.javaClass.name}'. Use default converter"
            }
            input.toString()
        }
    }

    private fun registerDate(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.string()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (field.typeName().equals("DATE", ignoreCase = true)) {
                return@register DateTimeConverter.convertToDate(input)
            }
            DateTimeConverter.convertToTimestamp(input)
        }
    }

    private fun registerDateTimeOffSet(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.string()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (input is DateTimeOffset) {
                val offsetDateTime = (input).offsetDateTime
                return@register offsetDateTime.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER)
            }

            LOGGER.warn {
                "Uncovered DateTimeOffSet class type '${input.javaClass.name}'. Use default converter"
            }
            input.toString()
        }
    }

    private fun registerDatetime(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.string()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (input is Timestamp) {
                val localDateTime: LocalDateTime = input.toLocalDateTime()
                return@register localDateTime.format(DateTimeFormatter.ofPattern(DATETIME_FORMAT_MICROSECONDS))
            }

            if (input is Long) {
                // During schema history creation datetime input arrives in the form of epoch nanosecond
                // This is needed for example for a column defined as:
                // [TransactionDate] DATETIME2 (7) DEFAULT ('2024-01-01T00:00:00.0000000') NOT NULL
                val instant = Instant.ofEpochMilli(input / 1000 / 1000)
                val localDateTime = LocalDateTime.ofInstant(instant, ZoneId.of("UTC"))
                return@register localDateTime.format(DateTimeFormatter.ofPattern(DATETIME_FORMAT_MICROSECONDS))
            }
            return@register input.toString()
        }
    }


    private fun registerTime(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.string()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (input is Timestamp) {
                return@register DateTimeFormatter.ISO_TIME.format((input).toLocalDateTime())
            }

            LOGGER.warn {
                "Uncovered time class type '${input.javaClass.name}'. Use default converter"
            }
            input.toString()
        }
    }

    private fun registerMoney(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.float64()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (input is BigDecimal) {
                return@register (input).toDouble()
            }

            LOGGER.warn {
                "Uncovered money class type '${input.javaClass.name}'. Use default converter"
            }
            input.toString()
        }
    }

    private fun registerBinary(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>
    ) {
        registration.register(SchemaBuilder.string()) { input: Any ->
            if (Objects.isNull(input)) {
                return@register convertDefaultValue(field)
            }
            if (input is ByteArray) {
                return@register Base64.getEncoder().encodeToString(input)
            }

            LOGGER.warn{
                "Uncovered binary class type '${input.javaClass.name}'. Use default converter"
            }
            input.toString()
        }
    }


    companion object {
        private val BINARY = setOf("VARBINARY", "BINARY")
        private val DATETIME_TYPES = setOf("DATETIME", "DATETIME2", "SMALLDATETIME")
        private const val DATE = "DATE"
        private const val DATETIMEOFFSET = "DATETIMEOFFSET"
        private const val TIME_TYPE = "TIME"
        private const val SMALLMONEY_TYPE = "SMALLMONEY"
        private const val GEOMETRY = "GEOMETRY"
        private const val GEOGRAPHY = "GEOGRAPHY"

        private const val DATETIME_FORMAT_MICROSECONDS = "yyyy-MM-dd'T'HH:mm:ss[.][SSSSSS]"
        private val LOGGER = KotlinLogging.logger {  }

        fun convertDefaultValue(field: RelationalColumn): Any? {
            if (field.isOptional) {
                return null
            } else if (field.hasDefaultValue()) {
                return field.defaultValue()
            }
            return null
        }
    }
}
