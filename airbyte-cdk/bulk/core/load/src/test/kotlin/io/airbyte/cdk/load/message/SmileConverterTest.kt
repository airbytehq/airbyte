/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.core.util.MinimalPrettyPrinter
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.MapperFeature.ACCEPT_CASE_INSENSITIVE_ENUMS
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.smile.databind.SmileMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.io.File
import java.nio.file.Files
import org.junit.jupiter.api.Test

class SmileConverterTest {

    private fun initSmileMapper(): ObjectMapper = configure(SmileMapper())

    private fun configure(objectMapper: ObjectMapper): ObjectMapper {
        objectMapper
            .enable(ACCEPT_CASE_INSENSITIVE_ENUMS)
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
            .configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
            .registerModule(JavaTimeModule())
            .registerModule(AfterburnerModule())
        return objectMapper
    }

    val SMILE_WRITER =
        initSmileMapper()
            .writerFor(AirbyteMessage::class.java)
            .with(MinimalPrettyPrinter(System.lineSeparator()))

    val jsonlFile =
        javaClass.getResource("/test-data-1-stream-100k-rows.json")
            ?: error("test-data-1-stream-100k-rows.jsonl not found")
    val outFile = File("test-data-1-stream-100k.smile3")
    val outputStream = Files.newOutputStream(outFile.toPath())

    @Test
    fun `make them smile`() {
        outputStream.use { outputStream ->
            jsonlFile.openStream().bufferedReader().use { reader ->
                reader.lineSequence().forEach { line ->
                    val abMessage = line.deserializeToClass(AirbyteMessage::class.java)
                    val smile = SMILE_WRITER.writeValueAsBytes(abMessage)
                    outputStream.write(smile)
                }
            }
        }
    }
}
