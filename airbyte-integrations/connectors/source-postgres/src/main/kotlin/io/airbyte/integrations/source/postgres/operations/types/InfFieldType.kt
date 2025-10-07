/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcGetter
import io.airbyte.cdk.jdbc.JdbcSetter
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.output.sockets.ConnectorJsonEncoder
import io.airbyte.cdk.output.sockets.ProtoEncoder
import io.airbyte.cdk.output.sockets.toProtobufEncoder
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import java.sql.PreparedStatement
import java.sql.ResultSet

// A generic field type which preserves infinity, -infinity and NaN values from DB to JSON
class InfFieldType<T>(
    airbyteSchemaType: AirbyteSchemaType,
    baseJdbcGetter: JdbcGetter<T>,
    baseJsonEncoder: JsonEncoder<T>,
    baseJsonDecoder: JsonDecoder<T>,
    baseJdbcSetter: JdbcSetter<in T>,
) :
    LosslessJdbcFieldType<InfWrapper<T>, InfWrapper<T>>(
        airbyteSchemaType,
        InfJdbcGetter(baseJdbcGetter),
        InfJsonEncoder(baseJsonEncoder),
        InfJsonDecoder(baseJsonDecoder),
        InfJdbcSetter(baseJdbcSetter),
    )

class InfJdbcGetter<T>(private val base: JdbcGetter<T>) : JdbcGetter<InfWrapper<T>> {
    override fun get(rs: ResultSet, colIdx: Int): InfWrapper<T> {
        return InfWrapper.make(rs, colIdx, base)
    }
}

class InfJdbcSetter<T>(private val base: JdbcSetter<in T>) : JdbcSetter<InfWrapper<T>> {
    override fun set(stmt: PreparedStatement, paramIdx: Int, value: InfWrapper<T>) {
        value.set(stmt, paramIdx, base)
    }
}

class InfJsonEncoder<T>(private val base: JsonEncoder<T>) :
    JsonEncoder<InfWrapper<T>>, ConnectorJsonEncoder {
    override fun encode(decoded: InfWrapper<T>): JsonNode {
        return decoded.encode(base)
    }

    override fun toProtobufEncoder(): ProtoEncoder<*> {
        return InfProtoEncoder(base)
    }
}

class InfJsonDecoder<T>(private val base: JsonDecoder<T>) : JsonDecoder<InfWrapper<T>> {
    override fun decode(encoded: JsonNode): InfWrapper<T> = InfWrapper.make(encoded, base)
}

class InfProtoEncoder<T>(private val base: JsonEncoder<T>) : ProtoEncoder<InfWrapper<T>> {
    override fun encode(
        builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder,
        decoded: InfWrapper<T>
    ): AirbyteRecordMessage.AirbyteValueProtobuf.Builder {
        @Suppress("UNCHECKED_CAST")
        return decoded.protoEncode(builder, base.toProtobufEncoder() as ProtoEncoder<T>)
    }
}

class InfWrapper<T>
private constructor(
    private val valueType: ValueType,
    private val normalValue: T? = null,
) {
    fun encode(baseEncoder: JsonEncoder<T>): JsonNode {
        if (valueType == ValueType.NORMAL) {
            return baseEncoder.encode(normalValue!!)
        }
        if (valueType == ValueType.NULL) {
            return NullNode.instance
        }
        return TextCodec.encode(valueType.placeholder!!)
    }

    fun set(stmt: PreparedStatement, paramIdx: Int, base: JdbcSetter<in T>) {
        if (valueType == ValueType.NORMAL) {
            base.set(stmt, paramIdx, normalValue!!)
        } else {
            stmt.setString(paramIdx, this.valueType.placeholder!!)
        }
    }

    @Suppress("UNCHECKED_CAST")
    fun protoEncode(
        builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder,
        baseEncoder: ProtoEncoder<T>
    ): AirbyteRecordMessage.AirbyteValueProtobuf.Builder {
        if (valueType == ValueType.NORMAL) {
            return baseEncoder.encode(builder, normalValue!!)
        }
        if (valueType == ValueType.NULL) {

            return (NullCodec.toProtobufEncoder() as ProtoEncoder<Any>).encode(
                builder,
                this
            ) // value doesn't matter
        }

        return (TextCodec.toProtobufEncoder() as ProtoEncoder<String>).encode(
            builder,
            valueType.placeholder!!
        )
    }

    companion object {
        fun <T> make(rs: ResultSet, colIdx: Int, baseGetter: JdbcGetter<T>): InfWrapper<T> {
            val str = rs.getString(colIdx) ?: return InfWrapper(ValueType.NULL)
            return if (str.equals(ValueType.INF.placeholder, ignoreCase = true)) {
                InfWrapper(ValueType.INF)
            } else if (str.equals(ValueType.MINUS_INF.placeholder, ignoreCase = true)) {
                InfWrapper(ValueType.MINUS_INF)
            } else if (str.equals(ValueType.NAN.placeholder, ignoreCase = true)) {
                InfWrapper(ValueType.NAN)
            } else {
                InfWrapper(ValueType.NORMAL, baseGetter.get(rs, colIdx))
            }
        }

        fun <T> make(encoded: JsonNode, base: JsonDecoder<T>): InfWrapper<T> {
            if (encoded.isNull) {
                return InfWrapper(ValueType.NULL)
            }
            if (encoded.isTextual) {
                val str = encoded.asText()
                return if (str.equals(ValueType.INF.placeholder, ignoreCase = true)) {
                    InfWrapper(ValueType.INF)
                } else if (str.equals(ValueType.MINUS_INF.placeholder, ignoreCase = true)) {
                    InfWrapper(ValueType.MINUS_INF)
                } else if (str.equals(ValueType.NAN.placeholder, ignoreCase = true)) {
                    InfWrapper(ValueType.NAN)
                } else {
                    InfWrapper(ValueType.NORMAL, base.decode(encoded))
                }
            }
            return InfWrapper(ValueType.NORMAL, base.decode(encoded))
        }
    }

    enum class ValueType(val placeholder: String? = null) {
        INF("Infinity"),
        MINUS_INF("-Infinity"),
        NAN("NaN"),
        NORMAL,
        NULL,
    }
}
