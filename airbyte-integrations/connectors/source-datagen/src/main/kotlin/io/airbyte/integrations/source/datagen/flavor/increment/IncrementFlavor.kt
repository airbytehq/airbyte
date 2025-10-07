/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.integrations.source.datagen.flavor.Flavor

data object IncrementFlavor : Flavor {
    val incrementTableName = "increment"

    override val namespace = "increment"
    override val tableNames = setOf(incrementTableName)
    override val fields =
        mapOf(
            incrementTableName to
                listOf(
                    Field("id", IntegerFieldType),
                    Field("string", StringFieldType)
                )
        )
    override val primaryKeys = mapOf(incrementTableName to listOf(listOf(("id"))))

    override val dataGenerator = IncrementDataGenerator()
}

data object IntegerFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = LongCodec
}

data object StringFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING
    override val jsonEncoder: JsonEncoder<*> = TextCodec
}
