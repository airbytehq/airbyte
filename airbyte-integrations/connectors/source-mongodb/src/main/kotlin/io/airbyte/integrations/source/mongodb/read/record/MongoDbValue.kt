/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.util.RawValue
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal

/**
 * A field value as the connector emits it, in the cheapest form each output channel takes: a scalar
 * as the JVM value the protobuf encoder wants, a document or array as the JSON text written once
 * while reading the BSON, which the JSON channel copies verbatim.
 */
sealed interface MongoDbValue {
    /** The JSON channel's node. */
    fun toJsonNode(): JsonNode

    /** The value as JSON text, as the JSON channel writes it. */
    fun toJsonText(): String

    class Text(val value: String) : MongoDbValue {
        override fun toJsonNode(): JsonNode = Jsons.textNode(value)

        override fun toJsonText(): String = Jsons.writeValueAsString(value)
    }

    /** A finite [Int], [Long], [Double] or [BigDecimal]. */
    class Num(val value: Number) : MongoDbValue {
        override fun toJsonNode(): JsonNode = Jsons.numberNode(value)

        override fun toJsonText(): String =
            if (value is BigDecimal) value.toPlainString() else value.toString()

        fun toBigDecimal(): BigDecimal =
            when (value) {
                is BigDecimal -> value
                is Double -> BigDecimal.valueOf(value)
                else -> BigDecimal.valueOf(value.toLong())
            }
    }

    class Bool(val value: Boolean) : MongoDbValue {
        override fun toJsonNode(): JsonNode = Jsons.booleanNode(value)

        override fun toJsonText(): String = value.toString()
    }

    object Null : MongoDbValue {
        override fun toJsonNode(): JsonNode = Jsons.nullNode()

        override fun toJsonText(): String = "null"
    }

    /** A document or an array, already written as compact JSON. */
    class Json(val text: String, val isArray: Boolean) : MongoDbValue {
        override fun toJsonNode(): JsonNode = Jsons.nodeFactory.rawValueNode(RawValue(text))

        override fun toJsonText(): String = text
    }
}
