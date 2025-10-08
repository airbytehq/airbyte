package io.airbyte.integrations.source.datagen

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.AnyEncoder
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BigDecimalIntegerCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.LongCodec
//import io.airbyte.cdk.data.ObjectAirbyteSchemaType
//import io.airbyte.cdk.data.ObjectEncoder
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.TextCodec
//import io.airbyte.cdk.data.UnknownAirbyteSchemaType
import io.airbyte.cdk.discover.FieldType

data object IntegerFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = IntCodec
}

data object BigIntegerFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = BigDecimalIntegerCodec
}

data object NumberFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.NUMBER
    override val jsonEncoder: JsonEncoder<*> = DoubleCodec
}

data object BigDecimalFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.NUMBER
    override val jsonEncoder: JsonEncoder<*> = BigDecimalCodec
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

data object JsonFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.JSONB
    override val jsonEncoder: JsonEncoder<*> = JsonStringCodec
}

 data class ArrayFieldType(val elementFieldType: FieldType) : FieldType {
     override val airbyteSchemaType: AirbyteSchemaType =
         ArrayAirbyteSchemaType(elementFieldType.airbyteSchemaType)
     override val jsonEncoder: JsonEncoder<*> = ArrayEncoder(elementFieldType.jsonEncoder)
 }

 //  TODO: left off here
 data class UnionFieldType(val options: Set<FieldType>,
                            val isLegacyUnion: Boolean,) : FieldType {
     override val airbyteSchemaType: AirbyteSchemaType = TODO()
     override val jsonEncoder: JsonEncoder<*> = TODO()
 }

// data class ObjectFieldType(
//     val properties: LinkedHashMap<String, FieldType>? = emptyMap(),
//     val additionalProperties: Boolean = true, // should this be here
//     val required: List<String> = emptyList()// should this be here
// ): FieldType {
//     val schemaMap: LinkedHashMap<String, AirbyteSchemaType> =
//         LinkedHashMap(properties.mapValues { it.value.airbyteSchemaType })
//     override val airbyteSchemaType: AirbyteSchemaType =
//         ObjectAirbyteSchemaType(schemaMap, additionalProperties, required)
//     val propertyEncoder: LinkedHashMap<String, JsonEncoder<*>> =
//         LinkedHashMap(properties.mapValues { it.value.jsonEncoder })
//     override val jsonEncoder: JsonEncoder<*> = ObjectEncoder(propertyEncoder)
// }
