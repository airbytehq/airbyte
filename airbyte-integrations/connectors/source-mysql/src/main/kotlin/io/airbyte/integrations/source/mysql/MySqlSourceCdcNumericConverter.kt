/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import java.util.*
import org.apache.kafka.connect.data.SchemaBuilder

class MySqlSourceCdcNumericConverter : CustomConverter<SchemaBuilder, RelationalColumn> {
    override fun configure(props: Properties?) {}

    private val NUMERIC_TYPES = arrayOf("FLOAT", "DOUBLE", "DECIMAL")

    override fun converterFor(
        field: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        if (
            Arrays.stream(NUMERIC_TYPES).anyMatch { s: String ->
                field!!.typeName().contains(s, ignoreCase = true)
            }
        ) {
            registerNumber(field, registration)
        }
    }

    private fun registerNumber(
        field: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        registration?.register(SchemaBuilder.float64()) { x ->
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
                is String -> x.toDouble()
                is Float -> x.toString().toDouble()
                is java.math.BigDecimal -> x.stripTrailingZeros().toDouble()
                is Number -> x.toDouble()
                else -> throw IllegalArgumentException("Unsupported type: ${x::class}")
            }
        }
    }
}
