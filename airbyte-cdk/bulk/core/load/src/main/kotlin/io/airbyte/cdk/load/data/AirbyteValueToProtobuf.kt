/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.google.protobuf.ByteString
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf

/** Convenience class for testing. */
class AirbyteValueToProtobuf {
    fun toProtobuf(value: AirbyteValue, type: AirbyteType): AirbyteValueProtobuf {
        val b = AirbyteValueProtobuf.newBuilder()
        if (value is NullValue) {
            return b.setIsNull(true).build()
        }
        fun setJson(value: AirbyteValue) =
            b.setJson(ByteString.copyFrom(value.toJson().serializeToJsonBytes()))
        when (type) {
            is BooleanType ->
                if (value is BooleanValue) b.setBoolean(value.value) else b.setIsNull(true)
            is StringType ->
                if (value is StringValue) b.setString(value.value) else b.setIsNull(true)
            is NumberType ->
                if (value is NumberValue) {
                    if (value.value.equals(value.value.toDouble())) {
                        b.setNumber(value.value.toDouble())
                    } else {
                        b.setBigDecimal(value.value.toString())
                    }
                } else {
                    setJson(value)
                }
            is IntegerType ->
                if (value is IntegerValue) {
                    if (value.value.equals(value.value.toLong())) {
                        b.setInteger(value.value.toLong())
                    } else {
                        b.setBigInteger(value.value.toString())
                    }
                } else {
                    b.setIsNull(true)
                }
            is DateType -> if (value is StringValue) b.setDate(value.value) else b.setIsNull(true)
            is TimeTypeWithTimezone ->
                if (value is StringValue) b.setTimeWithTimezone(value.value) else b.setIsNull(true)
            is TimeTypeWithoutTimezone ->
                if (value is StringValue) b.setTimeWithoutTimezone(value.value)
                else b.setIsNull(true)
            is TimestampTypeWithTimezone ->
                if (value is StringValue) {
                    b.setTimestampWithTimezone(value.value)
                } else {
                    b.setIsNull(true)
                }
            is TimestampTypeWithoutTimezone ->
                if (value is StringValue) {
                    b.setTimestampWithoutTimezone(value.value)
                } else {
                    b.setIsNull(true)
                }
            is ArrayType,
            ArrayTypeWithoutSchema ->
                if (value is ArrayValue) {
                    b.setJson(ByteString.copyFrom(value.toJson().serializeToJsonBytes()))
                } else {
                    b.setIsNull(true)
                }
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema ->
                if (value is ObjectValue) {
                    b.setJson(ByteString.copyFrom(value.toJson().serializeToJsonBytes()))
                } else {
                    b.setIsNull(true)
                }
            is UnionType,
            is UnknownType -> b.setJson(ByteString.copyFrom(value.toJson().serializeToJsonBytes()))
        }

        return b.build()
    }
}
