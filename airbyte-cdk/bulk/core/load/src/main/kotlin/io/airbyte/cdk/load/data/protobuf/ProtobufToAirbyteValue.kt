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
import io.airbyte.cdk.load.data.UnknownType
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
        val convertedFields = fields.associate { field -> field.name to convertField(proxy, field) }
        return ObjectValue(LinkedHashMap(convertedFields))
    }

    private fun convertField(
        proxy: AirbyteValueProxy,
        field: AirbyteValueProxy.FieldAccessor
    ): AirbyteValue {
        return when (field.type) {
            is BooleanType -> convertPrimitiveField { proxy.getBoolean(field) }?.let(::BooleanValue)
                    ?: NullValue
            is IntegerType -> convertPrimitiveField { proxy.getInteger(field) }?.let(::IntegerValue)
                    ?: NullValue
            is NumberType -> convertPrimitiveField { proxy.getNumber(field) }?.let(::NumberValue)
                    ?: NullValue
            is DateType -> convertPrimitiveField { proxy.getDate(field) }?.let(::DateValue)
                    ?: NullValue
            is StringType -> convertPrimitiveField { proxy.getString(field) }?.let(::StringValue)
                    ?: NullValue
            is TimeTypeWithTimezone ->
                convertPrimitiveField { proxy.getTimeWithTimezone(field) }
                    ?.let(::TimeWithTimezoneValue)
                    ?: NullValue
            is TimeTypeWithoutTimezone ->
                convertPrimitiveField { proxy.getTimeWithoutTimezone(field) }
                    ?.let(::TimeWithoutTimezoneValue)
                    ?: NullValue
            is TimestampTypeWithTimezone ->
                convertPrimitiveField { proxy.getTimestampWithTimezone(field) }
                    ?.let(::TimestampWithTimezoneValue)
                    ?: NullValue
            is TimestampTypeWithoutTimezone ->
                convertPrimitiveField { proxy.getTimestampWithoutTimezone(field) }
                    ?.let(::TimestampWithoutTimezoneValue)
                    ?: NullValue
            is ArrayType,
            is ArrayTypeWithoutSchema,
            is UnionType,
            is ObjectType,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema -> convertComplexField(proxy, field)
            is UnknownType -> NullValue
        }
    }

    private inline fun <T> convertPrimitiveField(getter: () -> T?): T? = getter()

    private fun convertComplexField(
        proxy: AirbyteValueProxy,
        field: AirbyteValueProxy.FieldAccessor
    ): AirbyteValue {
        val jsonNode = proxy.getJsonNode(field)
        return if (jsonNode != null) {
            jsonToAirbyteValue.convert(jsonNode)
        } else {
            NullValue
        }
    }
}

fun DestinationRecordProtobufSource.toAirbyteValue(
    fields: Array<AirbyteValueProxy.FieldAccessor>
): AirbyteValue {
    return ProtobufToAirbyteValue(fields = fields).convert(this)
}
