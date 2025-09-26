package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.AnyEncoder
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.ObjectEncoder
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.FieldType

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

// data object DateFieldType : FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.DATE
//     override val jsonEncoder: JsonEncoder<*> = LocalDateCodec
// }
// 
// data object TimeWithTimeZoneFieldType : FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
//     override val jsonEncoder: JsonEncoder<*> = OffsetTimeCodec
// }
// 
// data object TimeWithoutTimeZoneFieldType : FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
//     override val jsonEncoder: JsonEncoder<*> = LocalTimeCodec
// }
// 
// data object TimestampWithTimeZoneFieldType : FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
//     override val jsonEncoder: JsonEncoder<*> = OffsetDateTimeCodec
// }
// 
// data object TimestampWithoutTimeZoneFieldType : FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
//     override val jsonEncoder: JsonEncoder<*> = LocalDateTimeCodec
// }
// 
// data class ArrayFieldType(val elementFieldType: FieldType) : FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType =
//         ArrayAirbyteSchemaType(elementFieldType.airbyteSchemaType)
//     override val jsonEncoder: JsonEncoder<*> = ArrayEncoder(elementFieldType.jsonEncoder)
// }
// 
 data object ArrayWithoutSchemaFieldType : FieldType {
     override val airbyteSchemaType: AirbyteSchemaType = ArrayAirbyteSchemaType()
     override val jsonEncoder: JsonEncoder<*> = ArrayEncoder(AnyEncoder)
 }

// //  TODO: left off here
// data class UnionFieldType(val options: Set<FieldType>,
//                            val isLegacyUnion: Boolean,) : FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType = TODO()
//     override val jsonEncoder: JsonEncoder<*> = TODO()
// }
// 
 data class ObjectFieldType(
     val properties: LinkedHashMap<String, FieldType>,
     val additionalProperties: Boolean, // should this be here
     val required: List<String> // should this be here
 ) : FieldType {
     val schemaMap: LinkedHashMap<String, AirbyteSchemaType> =
         LinkedHashMap(properties.mapValues { (_, fieldType) ->
             fieldType.airbyteSchemaType
         })
     override val airbyteSchemaType: AirbyteSchemaType = ObjectAirbyteSchemaType(schemaMap, additionalProperties, required)
     val propertyEncoder: LinkedHashMap<String, JsonEncoder<*>> =
         LinkedHashMap(properties.mapValues { (k, v) ->
             v.jsonEncoder
         })
     override val jsonEncoder: JsonEncoder<*> = ObjectEncoder(propertyEncoder)
 }

 data class ObjectWithEmptySchemaFieldType(
     val propertiesEmpty: LinkedHashMap<String, AirbyteSchemaType> = LinkedHashMap(),
     val additionalProperties: Boolean,
     val required: List<String>
 ) : FieldType {
     override val airbyteSchemaType: AirbyteSchemaType = ObjectAirbyteSchemaType(propertiesEmpty, additionalProperties, required)
     override val jsonEncoder: JsonEncoder<*> = ObjectEncoder(LinkedHashMap<String, JsonEncoder<*>>())
 }

 data object ObjectWithoutSchemaFieldType : FieldType {
     override val airbyteSchemaType: AirbyteSchemaType = ObjectAirbyteSchemaType()
     override val jsonEncoder: JsonEncoder<*> = ObjectEncoder()
 }
// 
// data class UnknownFieldType(val schema: JsonNode): FieldType {
//     override val airbyteSchemaType: AirbyteSchemaType = UnknownAirbyteSchemaType(schema)
//     override val jsonEncoder: JsonEncoder<*> = AnyEncoder
// }
