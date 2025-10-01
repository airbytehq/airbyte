package io.airbyte.integrations.source.datagen.flavor.all_types

import io.airbyte.cdk.discover.Field
import io.airbyte.integrations.source.datagen.ArrayFieldType
import io.airbyte.integrations.source.datagen.ArrayWithoutSchemaFieldType
import io.airbyte.integrations.source.datagen.BooleanFieldType
import io.airbyte.integrations.source.datagen.DateFieldType
import io.airbyte.integrations.source.datagen.IntegerFieldType
import io.airbyte.integrations.source.datagen.ObjectFieldType
import io.airbyte.integrations.source.datagen.ObjectWithEmptySchemaFieldType
import io.airbyte.integrations.source.datagen.ObjectWithoutSchemaFieldType
import io.airbyte.integrations.source.datagen.StringFieldType
import io.airbyte.integrations.source.datagen.TimeWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimeWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithTimeZoneFieldType
import io.airbyte.integrations.source.datagen.TimestampWithoutTimeZoneFieldType
import io.airbyte.integrations.source.datagen.flavor.Flavor

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
                    Field("array without schema", ArrayWithoutSchemaFieldType),
                    Field("object", ObjectFieldType(
                        linkedMapOf(
                            "id" to IntegerFieldType,
                            "name" to StringFieldType)
                        )
                    ),
                    Field("object with empty schema", ObjectWithEmptySchemaFieldType()),
                    Field("object without schema", ObjectWithoutSchemaFieldType),
                )
        )
    override val primaryKeys = mapOf(typesTableName to listOf(listOf(("id"))))

    override val dataGenerator = TypesDataGenerator()
}
