/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeType
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.util.serializeToString
import java.math.BigDecimal
import java.math.BigInteger

class AirbyteValueJsonlProxy(private val data: ObjectNode) : AirbyteValueProxy {
    @Suppress("UNCHECKED_CAST")
    private fun <T> coerce(value: JsonNode?, type: AirbyteType): T? =
        when (type) {
            is ArrayType,
            is ArrayTypeWithoutSchema -> {
                when (value?.nodeType) {
                    JsonNodeType.ARRAY -> value
                    else -> null
                }
            }
            is BooleanType -> {
                when (value?.nodeType) {
                    JsonNodeType.BOOLEAN -> value.asBoolean()
                    JsonNodeType.NUMBER -> value.asBoolean()
                    JsonNodeType.STRING -> value.asText().toBooleanStrict()
                    else -> null
                }
            }
            is IntegerType -> {
                when (value?.nodeType) {
                    JsonNodeType.NUMBER -> value.bigIntegerValue()
                    JsonNodeType.STRING -> BigInteger(value.asText())
                    else -> null
                }
            }
            is NumberType -> {
                when (value?.nodeType) {
                    JsonNodeType.NUMBER -> value.decimalValue()
                    JsonNodeType.STRING -> BigDecimal(value.asText())
                    else -> null
                }
            }
            is ObjectType,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema ->
                when (value?.nodeType) {
                    JsonNodeType.OBJECT -> value
                    else -> null
                }
            is StringType -> {
                when (value?.nodeType) {
                    JsonNodeType.STRING -> value.asText()
                    JsonNodeType.NUMBER -> {
                        if (value.isIntegralNumber) {
                            value.decimalValue()
                        } else {
                            value.bigIntegerValue()
                        }
                    }
                    JsonNodeType.BOOLEAN -> value.asText().toBooleanStrict()
                    JsonNodeType.ARRAY,
                    JsonNodeType.OBJECT -> value.serializeToString()
                    else -> null
                }
            }
            else -> value
        }
            as T?

    private inline fun <T> getNullable(field: FieldAccessor, getter: (FieldAccessor) -> T): T? =
        data.get(field.name)?.let {
            if (
                it.isNull || it.nodeType == JsonNodeType.NULL || it.nodeType == JsonNodeType.MISSING
            )
                null
            else getter(field)
        }

    override fun getBoolean(field: FieldAccessor): Boolean? =
        getNullable(field) { coerce(value = data.get(it.name), type = field.type) }

    override fun getString(field: FieldAccessor): String? =
        getNullable(field) { coerce(value = data.get(it.name), type = field.type) }

    override fun getInteger(field: FieldAccessor): BigInteger? =
        getNullable(field) { coerce(value = data.get(it.name), type = field.type) }

    override fun getNumber(field: FieldAccessor): BigDecimal? =
        getNullable(field) { coerce(value = data.get(it.name), type = field.type) }

    override fun getDate(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimeWithTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimeWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimestampWithTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getTimestampWithoutTimezone(field: FieldAccessor): String? =
        getNullable(field) { data.get(it.name).asText() }

    override fun getJsonBytes(field: FieldAccessor): ByteArray? =
        getNullable(field) { data.get(it.name).serializeToJsonBytes() }

    override fun getJsonNode(field: FieldAccessor): JsonNode? =
        getNullable(field) { coerce(value = data.get(it.name), type = field.type) }

    override fun getJsonNode(field: String): JsonNode? = data.get(field)

    override fun undeclaredFields(declaredFields: Array<FieldAccessor>): Set<String> =
        data
            .fields()
            .asSequence()
            .filter { field ->
                declaredFields.find { declaredField -> declaredField.name == field.key } == null
            }
            .map { field -> field.key }
            .toSet()

    override fun hasField(field: FieldAccessor): Boolean = data.get(field.name) != null
}
