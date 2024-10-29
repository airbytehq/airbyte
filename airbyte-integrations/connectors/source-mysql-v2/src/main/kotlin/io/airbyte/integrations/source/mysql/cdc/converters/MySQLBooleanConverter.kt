/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc.converters

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import java.util.*
import org.apache.kafka.connect.data.SchemaBuilder

class MySQLBooleanConverter : CustomConverter<SchemaBuilder, RelationalColumn> {
    override fun configure(props: Properties?) {}

    private val BOOLEAN_TYPES = arrayOf("BOOLEAN", "BOOL", "TINYINT")

    override fun converterFor(
        field: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        if (
            Arrays.stream(BOOLEAN_TYPES).anyMatch { s: String ->
                field!!.typeName().contains(s, ignoreCase = true) &&
                    field.length().isPresent &&
                    field.length().asInt == 1
            }
        ) {
            registerBoolean(field, registration)
        }
    }

    private fun registerBoolean(
        field: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        registration?.register(SchemaBuilder.bool()) { x ->
            if (x == null) {
                return@register if (field!!.isOptional) {
                    null
                } else if (field.hasDefaultValue()) {
                    field.defaultValue()
                } else {
                    null
                }
            }
            when (x) {
                is Boolean -> x
                is String -> x.toBoolean()
                is Int -> x != 0
                else -> throw IllegalArgumentException("Unsupported type: ${x::class}")
            }
        }
    }
}
