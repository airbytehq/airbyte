/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.DestinationConfig
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
import java.io.File
import java.io.InputStream
import org.apache.avro.file.DataFileReader
import org.apache.avro.file.SeekableByteArrayInput
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericDatumReader
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class AvroSerializedBufferTest() {
    @Test
    @Disabled(
        "Flaky on CI, See run https://github.com/airbytehq/airbyte/actions/runs/7126781640/job/19405426141?pr=33201 " +
            "org.opentest4j.AssertionFailedError: Expected size between 964 and 985, but actual size was 991 ==> expected: <true> but was: <false>",
    )
    @Throws(
        Exception::class,
    )
    internal fun testSnappyAvroWriter() {
        val config =
            UploadAvroFormatConfig(
                Jsons.jsonNode(
                    mapOf(
                        "compression_codec" to mapOf("codec" to "snappy"),
                    ),
                ),
            )
        runTest(
            InMemoryBuffer(
                AvroSerializedBuffer.DEFAULT_SUFFIX,
            ),
            964L,
            985L,
            config,
            expectedString,
        )
    }

    @Test
    @Throws(Exception::class)
    internal fun testGzipAvroFileWriter() {
        val config =
            UploadAvroFormatConfig(
                Jsons.jsonNode(
                    mapOf(
                        "compression_codec" to
                            mapOf(
                                "codec" to "zstandard",
                                "compression_level" to 20,
                                "include_checksum" to true,
                            ),
                    ),
                ),
            )
        runTest(
            FileBuffer(
                AvroSerializedBuffer.DEFAULT_SUFFIX,
            ),
            965L,
            985L,
            config,
            expectedString,
        )
    }

    @Test
    @Throws(Exception::class)
    internal fun testUncompressedAvroWriter() {
        val config =
            UploadAvroFormatConfig(
                Jsons.jsonNode(
                    mapOf(
                        "compression_codec" to
                            mapOf(
                                "codec" to "no compression",
                            ),
                    ),
                ),
            )
        runTest(
            InMemoryBuffer(
                AvroSerializedBuffer.DEFAULT_SUFFIX,
            ),
            1010L,
            1020L,
            config,
            expectedString,
        )
    }

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
        private const val STREAM: String = "stream1"
        private val streamPair: AirbyteStreamNameNamespacePair =
            AirbyteStreamNameNamespacePair(
                STREAM,
                null,
            )
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
            CatalogHelpers.createConfiguredAirbyteCatalog(
                STREAM,
                null,
                FIELDS,
            )

        @BeforeAll
        @JvmStatic
        internal fun setup() {
            DestinationConfig.initialize(Jsons.deserialize("{}"))
        }

        private val expectedString: String
            get() =
                ("{\"_airbyte_ab_id\": \"<UUID>\", \"_airbyte_emitted_at\": \"<timestamp>\", " +
                    "\"field1\": 10000.0, \"another_field\": true, " +
                    "\"nested_column\": {\"_airbyte_additional_properties\": {\"array_column\": \"[1,2,3]\"}}, " +
                    "\"column2\": \"string value\", " +
                    "\"_airbyte_additional_properties\": null}")

        @Throws(Exception::class)
        private fun runTest(
            buffer: BufferStorage,
            minExpectedByte: Long,
            maxExpectedByte: Long,
            config: UploadAvroFormatConfig,
            expectedData: String
        ) {
            val outputFile: File = buffer.file
            (AvroSerializedBuffer.createFunction(config) { buffer }
                    .apply(
                        streamPair,
                        catalog,
                    ) as AvroSerializedBuffer)
                .use { writer ->
                    writer.accept(message)
                    writer.accept(message)
                    writer.flush()
                    // some data are randomized (uuid, timestamp, compression?) so the expected byte
                    // count is not always
                    // deterministic
                    assertTrue(
                        writer.byteCount in minExpectedByte..maxExpectedByte,
                        "Expected size between $minExpectedByte and $maxExpectedByte, but actual size was ${writer.byteCount}",
                    )
                    val `in`: InputStream = writer.inputStream!!
                    DataFileReader(
                            SeekableByteArrayInput(`in`.readAllBytes()),
                            GenericDatumReader<GenericData.Record>(),
                        )
                        .use { dataFileReader ->
                            while (dataFileReader.hasNext()) {
                                val record: GenericData.Record = dataFileReader.next()
                                record.put("_airbyte_ab_id", "<UUID>")
                                record.put("_airbyte_emitted_at", "<timestamp>")
                                val actualData: String = record.toString()
                                assertEquals(expectedData, actualData)
                            }
                        }
                }
            assertFalse(outputFile.exists())
        }
    }
}
