/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.util

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.core.StreamReadConstraints
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.BinaryNode
import com.fasterxml.jackson.databind.node.BooleanNode
import com.fasterxml.jackson.databind.node.NumericNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import com.fasterxml.jackson.module.kotlin.registerKotlinModule
import java.math.BigDecimal
import java.math.BigInteger
import java.nio.ByteBuffer

object Jsons : ObjectMapper() {
    // allow jackson to deserialize anything under 100 MiB
    // (the default, at time of writing 2024-05-29, with jackson 2.15.2, is 20 MiB)
    private const val JSON_MAX_LENGTH = 100 * 1024 * 1024

    init {
        registerKotlinModule()
        registerModule(JavaTimeModule())
        registerModule(AfterburnerModule())
        setSerializationInclusion(JsonInclude.Include.NON_NULL)
        configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
        configure(DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS, true)
        configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
        factory.setStreamReadConstraints(StreamReadConstraints.builder().maxStringLength(JSON_MAX_LENGTH).build())
    }

    fun objectNode(): ObjectNode = createObjectNode()

    fun arrayNode(): ArrayNode = createArrayNode()

    fun numberNode(n: Number): NumericNode =
        when (n) {
            is BigDecimal -> nodeFactory.numberNode(n) as NumericNode
            is BigInteger -> nodeFactory.numberNode(n) as NumericNode
            is Double -> nodeFactory.numberNode(n)
            is Float -> nodeFactory.numberNode(n)
            is Long -> nodeFactory.numberNode(n)
            is Int -> nodeFactory.numberNode(n)
            is Short -> nodeFactory.numberNode(n)
            is Byte -> nodeFactory.numberNode(n)
            else -> throw IllegalArgumentException("unsupported number class $${n::class} for $n")
        }

    fun textNode(str: CharSequence): TextNode = nodeFactory.textNode(str.toString())

    fun binaryNode(array: ByteArray): BinaryNode = nodeFactory.binaryNode(array)

    fun binaryNode(byteBuffer: ByteBuffer): BinaryNode {
        val array = ByteArray(byteBuffer.remaining()).also { byteBuffer.asReadOnlyBuffer().get(it) }
        return nodeFactory.binaryNode(array)
    }

    fun booleanNode(boolean: Boolean): BooleanNode = nodeFactory.booleanNode(boolean)
}
