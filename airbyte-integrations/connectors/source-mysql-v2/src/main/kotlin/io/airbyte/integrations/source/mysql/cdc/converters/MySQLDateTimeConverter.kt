/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc.converters

import io.airbyte.cdk.jdbc.converters.DateTimeConverter
import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.debezium.time.Conversions
import java.time.LocalDate
import java.time.LocalTime
import java.util.*
import java.util.concurrent.TimeUnit
import org.apache.kafka.connect.data.SchemaBuilder

/**
 * This is a custom debezium converter used in MySQL to handle the DATETIME data type. We need a
 * custom converter cause by default debezium returns the DATETIME values as numbers. We need to
 * convert it to proper format. Ref :
 * https://debezium.io/documentation/reference/2.1/development/converters.html This is built from
 * reference with {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter} If you
 * rename this class then remember to rename the datetime.type property value in {@link
 * MySqlCdcProperties#commonProperties(JdbcDatabase)} (If you don't rename, a test would still fail
 * but it might be tricky to figure out where to change the property name)
 */
class MySQLDateTimeConverter : CustomConverter<SchemaBuilder, RelationalColumn> {

    private val DATE_TYPES = arrayOf("DATE", "DATETIME", "TIME", "TIMESTAMP")
    override fun configure(props: Properties?) {}

    override fun converterFor(
        field: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        if (
            Arrays.stream<String>(DATE_TYPES).anyMatch { s: String ->
                s.equals(
                    field!!.typeName(),
                    ignoreCase = true,
                )
            }
        ) {
            registerDate(field, registration)
        }
    }

    private fun getTimePrecision(field: RelationalColumn): Int {
        return field.length().orElse(-1)
    }

    private fun registerDate(
        field: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        val fieldType = field!!.typeName()

        registration?.register(SchemaBuilder.string().optional()) { x ->
            if (x == null) {
                convertDefaultValue(field)
            }

            when (fieldType.uppercase()) {
                "DATETIME" -> {
                    if (x is Long) {
                        if (getTimePrecision(field) <= 3) {
                            DateTimeConverter.convertToTimestamp(
                                Conversions.toInstantFromMillis(x),
                            )
                        }
                        if (getTimePrecision(field) <= 6) {
                            DateTimeConverter.convertToTimestamp(
                                Conversions.toInstantFromMicros(x),
                            )
                        }
                    }
                    DateTimeConverter.convertToTimestamp(x)
                }
                "DATE" -> {
                    if (x is Int) {
                        DateTimeConverter.convertToDate(
                            LocalDate.ofEpochDay(
                                x.toLong(),
                            ),
                        )
                    }
                    DateTimeConverter.convertToDate(x)
                }
                "TIME" -> {
                    if (x is Long) {
                        val l = Math.multiplyExact(x, TimeUnit.MICROSECONDS.toNanos(1))
                        DateTimeConverter.convertToTime(
                            LocalTime.ofNanoOfDay(
                                l,
                            ),
                        )
                    }
                    DateTimeConverter.convertToTime(x)
                }
                "TIMESTAMP" ->
                    DateTimeConverter.convertToTimestampWithTimezone(
                        x,
                    )
                else ->
                    throw IllegalArgumentException("Unknown field type  " + fieldType.uppercase())
            }
        }
    }

    companion object {
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
