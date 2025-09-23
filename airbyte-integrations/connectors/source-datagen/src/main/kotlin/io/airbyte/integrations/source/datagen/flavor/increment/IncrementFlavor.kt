/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.AnyEncoder
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.integrations.source.datagen.flavor.Flavor

data object IncrementFlavor : Flavor {
    val incrementTableName = "increment"

    override val namespace = "increment"
    override val tableNames = setOf(incrementTableName)
    override val fields = mapOf(incrementTableName to
        listOf(Field("id", IntegerFieldType),
            Field("boolean", BooleanFieldType),
            Field("string", StringFieldType),))
    override val primaryKey = listOf("id")

//    val customSchema = fields.mapValues { (_, fields) ->
//        fields.filterNot { it.id == "boolean" } // user deselected "boolean"
//    }

    override val dataGenerator = IncrementDataGenerator(fields["increment"] ?: listOf(Field("id", IntegerFieldType)))
}

data object IntegerFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = LongCodec
}

data object BooleanFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN
    override val jsonEncoder: JsonEncoder<*> = BooleanCodec
}

data object StringFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING
    override val jsonEncoder: JsonEncoder<*> = TextCodec
}

data object DateFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.DATE
    override val jsonEncoder: JsonEncoder<*> = LocalDateCodec
}

data object TimeWithTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = OffsetTimeCodec
}

data object TimeWithoutTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalTimeCodec
}

data object TimestampWithTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = OffsetDateTimeCodec
}

data object TimestampWithoutTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalDateTimeCodec
}

data class ArrayFieldType(val elementFieldType: FieldType) : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType =
        ArrayAirbyteSchemaType(elementFieldType.airbyteSchemaType)
    override val jsonEncoder: JsonEncoder<*> = ArrayEncoder(elementFieldType.jsonEncoder)
}

data object ArrayWithoutSchemaFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = ArrayAirbyteSchemaType(Any)
    override val jsonEncoder: JsonEncoder<*> = ArrayEncoder(AnyEncoder)
}

data object UnionFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> =
}

data object ObjectFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalDateTimeCodec
}

data object ObjectWithEmptySchemaFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalDateTimeCodec
}

data object ObjectWithoutEmptySchemaFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalDateTimeCodec
}

data object UnknownFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalDateTimeCodec
}
