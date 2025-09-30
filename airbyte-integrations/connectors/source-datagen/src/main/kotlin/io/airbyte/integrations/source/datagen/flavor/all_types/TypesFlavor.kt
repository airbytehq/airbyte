package io.airbyte.integrations.source.datagen.flavor.all_types

import io.airbyte.cdk.discover.Field
import io.airbyte.integrations.source.datagen.ArrayFieldType
import io.airbyte.integrations.source.datagen.BooleanFieldType
import io.airbyte.integrations.source.datagen.DateFieldType
import io.airbyte.integrations.source.datagen.IntegerFieldType
import io.airbyte.integrations.source.datagen.StringFieldType
import io.airbyte.integrations.source.datagen.TimeWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimeWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.flavor.Flavor
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementDataGenerator

data object TypesFlavor : Flavor {
    val typesTableName = "all types"

    override val namespace = "all types"
    override val tableNames = setOf(typesTableName)
    override val fields =
        mapOf(
            typesTableName to
                listOf(
                    Field("id", IntegerFieldType),
                    Field("string", StringFieldType),
                    Field("boolean", BooleanFieldType),
                    Field("date", DateFieldType),
                    Field("time with time zone", TimeWithTimeZoneFieldType),
                    Field("time without time zone", TimeWithoutTimeZoneFieldType),
                    Field("timestamp with time zone", TimestampWithTimeZoneFieldType),
                    Field("timestamp without time zone", TimestampWithoutTimeZoneFieldType),
                    Field("array", ArrayFieldType(IntegerFieldType)),
                )
        )
    override val primaryKeys = mapOf(typesTableName to listOf(listOf(("id"))))

    override val dataGenerator = TypesDataGenerator()
}
