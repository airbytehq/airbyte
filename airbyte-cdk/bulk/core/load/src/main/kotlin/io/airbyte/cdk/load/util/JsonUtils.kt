/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.core.StreamReadConstraints
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import com.fasterxml.jackson.module.kotlin.registerKotlinModule
import java.io.InputStream

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
        factory.setStreamReadConstraints(
            StreamReadConstraints.builder().maxStringLength(JSON_MAX_LENGTH).build()
        )
    }
}

fun <T> T.serializeToString(): String {
    return Jsons.writeValueAsString(this)
}

fun <T> InputStream.readIntoClass(klass: Class<T>): T =
    Jsons.readTree(this).let { Jsons.treeToValue(it, klass) }

fun <T> T.deserializeToPrettyPrintedString(): String {
    return Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(this)
}

fun String.deserializeToNode(): JsonNode {
    return Jsons.readTree(this)
}

fun <T> String.deserializeToClass(klass: Class<T>): T {
    return Jsons.readValue(this, klass)
}

fun Any.serializeToJsonBytes(): ByteArray {
    return Jsons.writeValueAsBytes(this)
}
