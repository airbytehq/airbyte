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
import com.fasterxml.jackson.databind.cfg.JsonNodeFeature
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import com.fasterxml.jackson.module.kotlin.registerKotlinModule
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.json.toJson
import java.io.InputStream

object Jsons : ObjectMapper() {
    // allow jackson to deserialize anything under 100 MiB
    // (the default, at time of writing 2024-05-29, with jackson 2.15.2, is 20 MiB)
    private const val JSON_MAX_LENGTH = 100 * 1024 * 1024

    init {
        registerKotlinModule()
        registerModule(JavaTimeModule())
        registerModule(AfterburnerModule())
        registerModule(AirbyteValueModule)
        setSerializationInclusion(JsonInclude.Include.NON_NULL)
        configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
        configure(DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS, true)
        configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
        configure(JsonNodeFeature.STRIP_TRAILING_BIGDECIMAL_ZEROES, false)
        factory.setStreamReadConstraints(
            StreamReadConstraints.builder().maxStringLength(JSON_MAX_LENGTH).build()
        )
    }
}

/**
 * Serialises any `AirbyteValue` subtype by delegating to its `toJson()` helper. Works for
 * value-classes, object singletons, and normal classes.
 */
private object AirbyteValueModule : com.fasterxml.jackson.databind.module.SimpleModule() {

    init {
        // a single generic serializer is enough because all wrappers implement AirbyteValue
        addSerializer(
            AirbyteValue::class.java,
            object : com.fasterxml.jackson.databind.JsonSerializer<AirbyteValue>() {
                override fun serialize(
                    value: AirbyteValue,
                    gen: JsonGenerator,
                    serializers: com.fasterxml.jackson.databind.SerializerProvider
                ) {
                    when (value) {
                        is NullValue -> gen.writeNull() // special-case null
                        is ObjectValue ->
                            serializers.defaultSerializeValue(
                                value.toJson(),
                                gen
                            ) // Map<String,Any?>
                        is ArrayValue -> {
                            gen.writeStartArray()
                            value.values.forEach { serializers.defaultSerializeValue(it, gen) }
                            gen.writeEndArray()
                        }
                        else ->
                            serializers.defaultSerializeValue(
                                value.toJson(),
                                gen
                            ) // scalar wrappers
                    }
                }
            }
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
