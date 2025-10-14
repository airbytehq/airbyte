/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.types

import io.airbyte.cdk.discover.Field
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

data object TypesFlavor : Flavor {
    val typesTableName = "all types"

    object FieldNames {
        const val ID = "id"
        const val STRING = "string"
        const val BOOLEAN = "boolean"
        const val NUMBER = "number"
        const val BIG_INTEGER = "big integer"
        const val BIG_DECIMAL = "big decimal"
        const val DATE = "date"
        const val TIME_WITH_TIME_ZONE = "time with time zone"
        const val TIME_WITHOUT_TIME_ZONE = "time without time zone"
        const val TIMESTAMP_WITH_TIME_ZONE = "timestamp with time zone"
        const val TIMESTAMP_WITHOUT_TIME_ZONE = "timestamp without time zone"
        const val JSON = "json"
        const val ARRAY = "array"
    }

    override val namespace = "all types"
    override val tableNames = setOf(typesTableName)
    override val fields =
        mapOf(
            typesTableName to
                listOf(
                    Field(FieldNames.ID, IntegerFieldType),
                    Field(FieldNames.STRING, StringFieldType),
                    Field(FieldNames.BOOLEAN, BooleanFieldType),
                    Field(FieldNames.NUMBER, NumberFieldType),
                    Field(FieldNames.BIG_INTEGER, BigIntegerFieldType),
                    Field(FieldNames.BIG_DECIMAL, BigDecimalFieldType),
                    Field(FieldNames.DATE, DateFieldType),
                    Field(FieldNames.TIME_WITH_TIME_ZONE, TimeWithTimeZoneFieldType),
                    Field(FieldNames.TIME_WITHOUT_TIME_ZONE, TimeWithoutTimeZoneFieldType),
                    Field(FieldNames.TIMESTAMP_WITH_TIME_ZONE, TimestampWithTimeZoneFieldType),
                    Field(
                        FieldNames.TIMESTAMP_WITHOUT_TIME_ZONE,
                        TimestampWithoutTimeZoneFieldType
                    ),
                    Field(FieldNames.JSON, JsonFieldType),
                )
        )
    override val primaryKeys = mapOf(typesTableName to listOf(listOf((FieldNames.ID))))

    override val dataGenerator = TypesDataGenerator()
}
