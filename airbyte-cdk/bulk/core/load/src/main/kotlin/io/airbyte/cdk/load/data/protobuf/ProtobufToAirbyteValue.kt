/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.protobuf

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.json.JsonToAirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource

/**
 * Naively convert a Protocol Buffers object to the equivalent [AirbyteValue]. Note that this does
 * not match against a declared schema; it simply does the most obvious conversion.
 */
class ProtobufToAirbyteValue(
    private val fields: Array<AirbyteValueProxy.FieldAccessor>,
) {
    
    private val jsonToAirbyteValue = JsonToAirbyteValue()

    fun convert(record: DestinationRecordProtobufSource): AirbyteValue {
        val proxy = record.asAirbyteValueProxy()
        val values: LinkedHashMap<String, AirbyteValue> =
            LinkedHashMap(
                fields.associate { field ->
                    field.name to
                        when (field.type) {
                            is BooleanType ->
                                if (proxy.getBoolean(field) == null) NullValue
                                else BooleanValue(proxy.getBoolean(field)!!)
                            is IntegerType ->
                                if (proxy.getInteger(field) == null) NullValue
                                else IntegerValue(proxy.getInteger(field)!!)
                            is NumberType ->
                                if (proxy.getNumber(field) == null) NullValue
                                else NumberValue(proxy.getNumber(field)!!)
                            is DateType ->
                                if (proxy.getDate(field) == null) NullValue
                                else DateValue(proxy.getDate(field)!!)
                            is ArrayType,
                            is ArrayTypeWithoutSchema,
                            is UnionType,
                            is ObjectType,
                            is ObjectTypeWithEmptySchema,
                            is ObjectTypeWithoutSchema ->
                                if (proxy.getJsonNode(field) == null) NullValue
                                else jsonToAirbyteValue.convert(proxy.getJsonNode(field)!!)
                            is StringType ->
                                if (proxy.getString(field) == null) NullValue
                                else StringValue(proxy.getString(field)!!)
                            is TimeTypeWithTimezone ->
                                if (proxy.getTimeWithTimezone(field) == null) NullValue
                                else TimeWithTimezoneValue(proxy.getTimeWithTimezone(field)!!)
                            is TimeTypeWithoutTimezone ->
                                if (proxy.getTimeWithoutTimezone(field) == null) NullValue
                                else TimeWithoutTimezoneValue(proxy.getTimeWithoutTimezone(field)!!)
                            is TimestampTypeWithTimezone ->
                                if (proxy.getTimestampWithTimezone(field) == null) NullValue
                                else
                                    TimestampWithTimezoneValue(
                                        proxy.getTimestampWithTimezone(field)!!
                                    )
                            is TimestampTypeWithoutTimezone ->
                                if (proxy.getTimestampWithoutTimezone(field) == null) NullValue
                                else
                                    TimestampWithoutTimezoneValue(
                                        proxy.getTimestampWithoutTimezone(field)!!
                                    )
                            else -> NullValue
                        }
                }
            )
        return ObjectValue(values)
    }
}

fun DestinationRecordProtobufSource.toAirbyteValue(
    fields: Array<AirbyteValueProxy.FieldAccessor>
): AirbyteValue {
    return ProtobufToAirbyteValue(fields = fields).convert(this)
}
