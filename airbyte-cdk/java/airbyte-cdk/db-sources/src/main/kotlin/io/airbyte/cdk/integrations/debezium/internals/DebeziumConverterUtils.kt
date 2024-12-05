/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.airbyte.cdk.db.DataTypeUtils.toISO8601String
import io.airbyte.cdk.db.DataTypeUtils.toISO8601StringWithMicroseconds
import io.debezium.spi.converter.RelationalColumn
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Date
import java.sql.Timestamp
import java.time.Duration
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeParseException

private val LOGGER = KotlinLogging.logger {}

class DebeziumConverterUtils private constructor() {
    init {
        throw UnsupportedOperationException()
    }

    companion object {

        /** TODO : Replace usage of this method with [io.airbyte.cdk.db.jdbc.DateTimeConverter] */
        @JvmStatic
        fun convertDate(input: Any): String {
            /**
             * While building this custom converter we were not sure what type debezium could return
             * cause there is no mention of it in the documentation. Secondly if you take a look at
             * [io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter.converterFor]
             * method, even it is handling multiple data types but its not clear under what
             * circumstances which data type would be returned. I just went ahead and handled the
             * data types that made sense. Secondly, we use LocalDateTime to handle this cause it
             * represents DATETIME datatype in JAVA
             */
            if (input is LocalDateTime) {
                return toISO8601String(input)
            } else if (input is LocalDate) {
                return toISO8601String(input)
            } else if (input is Duration) {
                return toISO8601String(input)
            } else if (input is Timestamp) {
                return toISO8601StringWithMicroseconds((input.toInstant()))
            } else if (input is Number) {
                return toISO8601String(Timestamp(input.toLong()).toLocalDateTime())
            } else if (input is Date) {
                return toISO8601String(input)
            } else if (input is String) {
                try {
                    return LocalDateTime.parse(input).toString()
                } catch (e: DateTimeParseException) {
                    LOGGER.warn { "Cannot convert value '$input' to LocalDateTime type" }
                    return input.toString()
                }
            }
            LOGGER.warn {
                "Uncovered date class type '${input.javaClass.name}'. Use default converter"
            }
            return input.toString()
        }

        @JvmStatic
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
