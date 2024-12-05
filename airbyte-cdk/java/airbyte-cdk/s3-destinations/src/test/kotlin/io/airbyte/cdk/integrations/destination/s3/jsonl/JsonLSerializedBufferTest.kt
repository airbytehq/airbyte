/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonl

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.InMemoryBuffer
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.io.InputStream
import java.nio.charset.StandardCharsets
import java.util.zip.GZIPInputStream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class JsonLSerializedBufferTest {

    companion object {
        private val MESSAGE_DATA: JsonNode =
            Jsons.jsonNode(
                mapOf(
                    "field1" to 10000,
                    "column2" to "string value",
                    "another field" to true,
                    "nested_column" to mapOf("array_column" to listOf(1, 2, 3)),
                ),
            )
        private const val STREAM = "stream1"
        private val streamPair = AirbyteStreamNameNamespacePair(STREAM, null)
        private val message: AirbyteRecordMessage =
            AirbyteRecordMessage()
                .withStream(STREAM)
                .withData(MESSAGE_DATA)
                .withEmittedAt(System.currentTimeMillis())
        private val FIELDS: List<Field> =
            listOf(
                Field.of("field1", JsonSchemaType.NUMBER),
                Field.of("column2", JsonSchemaType.STRING),
                Field.of("another field", JsonSchemaType.BOOLEAN),
                Field.of("nested_column", JsonSchemaType.OBJECT),
            )
        private val catalog: ConfiguredAirbyteCatalog =
            CatalogHelpers.createConfiguredAirbyteCatalog(STREAM, null, FIELDS)
        private const val JSON_FILE_EXTENSION = ".jsonl"
    }

    @Test
    @Throws(Exception::class)
    internal fun testUncompressedJsonLFormatWriter() {
        runTest(InMemoryBuffer(JSON_FILE_EXTENSION), false, 425L, 435L, getExpectedString())
    }

    @Test
    @Throws(Exception::class)
    internal fun testCompressedJsonLWriter() {
        runTest(FileBuffer(JSON_FILE_EXTENSION), true, 205L, 215L, getExpectedString())
    }

    private fun getExpectedString(): String {
        return Jsons.serialize(MESSAGE_DATA)
    }

    @Throws(Exception::class)
    private fun runTest(
        buffer: BufferStorage,
        withCompression: Boolean,
        minExpectedByte: Long,
        maxExpectedByte: Long,
        expectedData: String
    ) {
        val outputFile = buffer.file
        (JsonLSerializedBuffer.createBufferFunction(null, { buffer })
                .apply(
                    streamPair,
                    catalog,
                ) as JsonLSerializedBuffer)
            .use { writer ->
                writer.withCompression(withCompression)
                writer.accept(message)
                writer.accept(message)
                writer.flush()
                // some data are randomized (uuid, timestamp, compression?) so the expected byte
                // count is not always
                // deterministic
                assertTrue(
                    writer.byteCount in minExpectedByte..maxExpectedByte,
                    "Expected size between $minExpectedByte and $maxExpectedByte, but actual size was ${writer.byteCount}"
                )
                val inputStream: InputStream =
                    if (withCompression) {
                        GZIPInputStream(writer.inputStream)
                    } else {
                        writer.inputStream!!
                    }
                val actualData =
                    Jsons.deserialize(String(inputStream.readAllBytes(), StandardCharsets.UTF_8))
                assertEquals(
                    expectedData,
                    Jsons.serialize(
                        actualData["_airbyte_data"],
                    ),
                )
            }
        assertFalse(outputFile.exists())
    }
}
