/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.wide

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.integrations.source.datagen.BigDecimalFieldType
import io.airbyte.integrations.source.datagen.BigIntegerFieldType
import io.airbyte.integrations.source.datagen.BooleanFieldType
import io.airbyte.integrations.source.datagen.DateFieldType
import io.airbyte.integrations.source.datagen.IntegerFieldType
import io.airbyte.integrations.source.datagen.JsonFieldType
import io.airbyte.integrations.source.datagen.NumberFieldType
import io.airbyte.integrations.source.datagen.StringFieldType
import io.airbyte.integrations.source.datagen.TimeWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimeWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.flavor.Flavor

class WideFlavor(columnCount: Int) : Flavor {
    companion object {
        private const val TABLE_NAME = "wide"

        val COLUMN_TYPES: List<Pair<String, FieldType>> = listOf(
            "integer" to IntegerFieldType,
            "string" to StringFieldType,
            "boolean" to BooleanFieldType,
            "number" to NumberFieldType,
            "big_integer" to BigIntegerFieldType,
            "big_decimal" to BigDecimalFieldType,
            "date" to DateFieldType,
            "time_with_tz" to TimeWithTimeZoneFieldType,
            "time_without_tz" to TimeWithoutTimeZoneFieldType,
            "timestamp_with_tz" to TimestampWithTimeZoneFieldType,
            "timestamp_without_tz" to TimestampWithoutTimeZoneFieldType,
            "json" to JsonFieldType,
        )
    }

    private val generatedFields: List<Field> = buildList {
        add(Field("id", IntegerFieldType))
        for (i in 1 until columnCount) {
            val typeIndex = (i - 1) % COLUMN_TYPES.size
            val (typeSuffix, fieldType) = COLUMN_TYPES[typeIndex]
            add(Field("col_${i}_$typeSuffix", fieldType))
        }
    }

    override val namespace = TABLE_NAME
    override val tableNames = setOf(TABLE_NAME)
    override val fields = mapOf(TABLE_NAME to generatedFields)
    override val primaryKeys = mapOf(TABLE_NAME to listOf(listOf("id")))
    override val dataGenerator = WideDataGenerator(generatedFields)
}
