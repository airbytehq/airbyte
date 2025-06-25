/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.json.JsonToAirbyteValue
import io.airbyte.cdk.util.Jsons.objectNode
import java.math.BigDecimal
import java.math.BigInteger

/**
 * Provides a universal view over raw data, agnostic of the serialization format. Fields are
 * accessed with accessors that contain name, index, and type. The type indicates with method should
 * be used.
 */
interface AirbyteValueProxy {
    fun getBoolean(field: FieldAccessor): Boolean?
    fun getString(field: FieldAccessor): String?
    fun getInteger(field: FieldAccessor): BigInteger?
    fun getNumber(field: FieldAccessor): BigDecimal?
    fun getDate(field: FieldAccessor): String?
    fun getTimeWithTimezone(field: FieldAccessor): String?
    fun getTimeWithoutTimezone(field: FieldAccessor): String?
    fun getTimestampWithTimezone(field: FieldAccessor): String?
    fun getTimestampWithoutTimezone(field: FieldAccessor): String?
    fun getJsonBytes(field: FieldAccessor): ByteArray?
    fun getJsonNode(field: FieldAccessor): JsonNode?
    fun getJsonNode(field: String): JsonNode?
    fun hasField(field: FieldAccessor): Boolean
    fun undeclaredFields(declaredFields: Array<FieldAccessor>): Set<String>
    data class FieldAccessor(val index: Int, val name: String, val type: AirbyteType)
}

// TODO: This should not be done for proto, takes away all the benefits of using proto
fun AirbyteValueProxy.asJson(orderedSchema: Array<FieldAccessor>): ObjectNode {
    val objectNode = JsonNodeFactory.instance.objectNode()
    orderedSchema.forEach {
        when (it.type) {
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithoutSchema,
            ObjectTypeWithEmptySchema,
            is UnionType,
            is UnknownType ->
                this.getJsonNode(it)?.let { v -> objectNode.set<JsonNode>(it.name, v) }
            BooleanType -> this.getBoolean(it)?.let { v -> objectNode.put(it.name, v) }
            IntegerType -> this.getInteger(it)?.let { v -> objectNode.put(it.name, v) }
            NumberType -> this.getNumber(it)?.let { v -> objectNode.put(it.name, v) }
            StringType -> this.getString(it)?.let { v -> objectNode.put(it.name, v) }
            DateType -> this.getDate(it)?.let { v -> objectNode.put(it.name, v) }
            TimeTypeWithTimezone ->
                this.getTimeWithTimezone(it)?.let { v -> objectNode.put(it.name, v) }
            TimeTypeWithoutTimezone ->
                this.getTimeWithoutTimezone(it)?.let { v -> objectNode.put(it.name, v) }
            TimestampTypeWithTimezone ->
                this.getTimestampWithTimezone(it)?.let { v -> objectNode.put(it.name, v) }
            TimestampTypeWithoutTimezone ->
                this.getTimestampWithoutTimezone(it)?.let { v -> objectNode.put(it.name, v) }
        }
    }
    return objectNode
}

fun AirbyteValueProxy.getAirbyteValue(field: FieldAccessor): AirbyteValue {
    val jsonToAirbyteValue = JsonToAirbyteValue()
    return when (field.type) {
        is ArrayType,
        is ArrayTypeWithoutSchema,
        is ObjectType,
        is ObjectTypeWithoutSchema,
        is ObjectTypeWithEmptySchema,
        is UnionType,
        is UnknownType -> this.getJsonNode(field)?.let { v -> jsonToAirbyteValue.convert(v) }
                ?: NullValue
        is BooleanType -> this.getBoolean(field)?.let { v -> BooleanValue(v) } ?: NullValue
        is IntegerType -> this.getInteger(field)?.let { v -> IntegerValue(v) } ?: NullValue
        is NumberType -> this.getNumber(field)?.let { v -> NumberValue(v) } ?: NullValue
        is StringType -> this.getString(field)?.let { v -> StringValue(v) } ?: NullValue
        is TimeTypeWithTimezone ->
            this.getTimeWithTimezone(field)?.let { v -> TimeWithTimezoneValue(v) } ?: NullValue
        is TimeTypeWithoutTimezone ->
            this.getTimeWithoutTimezone(field)?.let { v -> TimeWithoutTimezoneValue(v) }
                ?: NullValue
        is TimestampTypeWithTimezone ->
            this.getTimestampWithTimezone(field)?.let { v -> TimestampWithTimezoneValue(v) }
                ?: NullValue
        is TimestampTypeWithoutTimezone ->
            this.getTimestampWithoutTimezone(field)?.let { v -> TimestampWithoutTimezoneValue(v) }
                ?: NullValue
        is DateType -> this.getDate(field)?.let { v -> DateValue(v) } ?: NullValue
    }
}
