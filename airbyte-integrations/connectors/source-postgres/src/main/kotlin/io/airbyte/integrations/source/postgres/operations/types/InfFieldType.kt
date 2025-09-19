/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JdbcGetter
import java.sql.ResultSet

// A generic field type which preserves infinity, -infinity and NaN values from DB to JSON
class InfFieldType<T>(
    airbyteSchemaType: AirbyteSchemaType,
    baseJdbcGetter: JdbcGetter<T>,
    baseJsonEncoder: JsonEncoder<T>,
) :
    JdbcFieldType<InfWrapper<T>>(
        airbyteSchemaType,
        InfJdbcGetter(baseJdbcGetter),
        InfJsonEncoder(baseJsonEncoder),
    )

class InfJdbcGetter<T>(private val base: JdbcGetter<T>) : JdbcGetter<InfWrapper<T>> {
    override fun get(rs: ResultSet, colIdx: Int): InfWrapper<T>? {
        return InfWrapper.make(rs, colIdx, base)
    }
}

class InfJsonEncoder<T>(private val base: JsonEncoder<T>) : JsonEncoder<InfWrapper<T>> {
    override fun encode(decoded: InfWrapper<T>): JsonNode {
        return decoded.encode(base)
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

    companion object {
        fun <T> make(rs: ResultSet, colIdx: Int, baseGetter: JdbcGetter<T>): InfWrapper<T> {
            val str = rs.getString(colIdx) ?: return InfWrapper(ValueType.NULL)
            return if (str.lowercase() == "infinity") {
                InfWrapper(ValueType.INF)
            } else if (str.lowercase() == "-infinity") {
                InfWrapper(ValueType.MINUS_INF)
            } else if (str.lowercase() == "nan") {
                InfWrapper(ValueType.NAN)
            } else {
                InfWrapper(ValueType.NORMAL, baseGetter.get(rs, colIdx))
            }
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
