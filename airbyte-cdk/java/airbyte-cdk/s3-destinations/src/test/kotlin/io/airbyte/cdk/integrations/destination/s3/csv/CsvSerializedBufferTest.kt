/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.InMemoryBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.io.BufferedReader
import java.io.InputStream
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.util.UUID
import java.util.zip.GZIPInputStream
import org.apache.commons.csv.CSVFormat
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class CsvSerializedBufferTest {

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
        private const val CSV_FILE_EXTENSION = ".csv"
        private val csvFormat: CSVFormat = CSVFormat.newFormat(',')
    }

    @BeforeEach
    internal fun setup() {
        DestinationConfig.initialize(Jsons.emptyObject())
    }

    @Test
    @Throws(Exception::class)
    internal fun testUncompressedDefaultCsvFormatWriter() {
        runTest(
            InMemoryBuffer(CSV_FILE_EXTENSION),
            CSVFormat.DEFAULT,
            false,
            350L,
            365L,
            null,
            getExpectedString(CSVFormat.DEFAULT),
        )
    }

    @Test
    @Throws(Exception::class)
    internal fun testUncompressedCsvWriter() {
        runTest(
            InMemoryBuffer(CSV_FILE_EXTENSION),
            csvFormat,
            false,
            320L,
            335L,
            null,
            getExpectedString(csvFormat),
        )
    }

    @Test
    @Throws(Exception::class)
    internal fun testCompressedCsvWriter() {
        runTest(
            InMemoryBuffer(CSV_FILE_EXTENSION),
            csvFormat,
            true,
            170L,
            190L,
            null,
            getExpectedString(csvFormat),
        )
    }

    @Test
    @Throws(Exception::class)
    internal fun testCompressedCsvFileWriter() {
        runTest(
            FileBuffer(CSV_FILE_EXTENSION),
            csvFormat,
            true,
            170L,
            190L,
            null,
            getExpectedString(csvFormat),
        )
    }

    private fun getExpectedString(csvFormat: CSVFormat): String {
        var expectedData = Jsons.serialize(MESSAGE_DATA)
        if (csvFormat == CSVFormat.DEFAULT) {
            expectedData = "\"" + expectedData.replace("\"", "\"\"") + "\""
        }
        return expectedData
    }

    @Test
    @Throws(Exception::class)
    @Suppress("DEPRECATION")
    internal fun testFlattenCompressedCsvFileWriter() {
        val expectedData = "true,string value,10000,{\"array_column\":[1,2,3]}"
        runTest(
            FileBuffer(CSV_FILE_EXTENSION),
            CSVFormat.newFormat(',').withRecordSeparator('\n'),
            true,
            135L,
            150L,
            UploadCsvFormatConfig(
                Jsons.jsonNode(
                    mapOf(
                        "format_type" to FileUploadFormat.CSV,
                        "flattening" to Flattening.ROOT_LEVEL.value,
                    ),
                ),
            ),
            expectedData + expectedData,
        )
    }

    @Throws(Exception::class)
    private fun runTest(
        buffer: BufferStorage,
        csvFormat: CSVFormat,
        withCompression: Boolean,
        minExpectedByte: Long,
        maxExpectedByte: Long,
        config: UploadCsvFormatConfig?,
        expectedData: String
    ) {
        val outputFile = buffer.file
        val defaultNamespace = ""

        (CsvSerializedBuffer.createFunction(config, { buffer })
                .apply(
                    streamPair,
                    catalog,
                ) as CsvSerializedBuffer)
            .use { writer ->
                writer.withCsvFormat(csvFormat)
                writer.withCompression(withCompression)
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
                val inputStream: InputStream =
                    if (withCompression) {
                        GZIPInputStream(writer.inputStream)
                    } else {
                        writer.inputStream!!
                    }
                val actualData: String
                if (config == null) {
                    actualData =
                        String(
                                inputStream.readAllBytes(),
                                StandardCharsets.UTF_8,
                            )
                            .substring(
                                UUID.randomUUID().toString().length + 1,
                            ) // remove the last part of the string with random timestamp
                            .substring(0, expectedData.length)
                } else {
                    val reader =
                        BufferedReader(InputStreamReader(inputStream, StandardCharsets.UTF_8))
                    val tmpData = StringBuilder()
                    var line: String
                    while (reader.ready()) {
                        line = reader.readLine()
                        tmpData.append(
                            line // remove uuid
                                .substring(
                                    UUID.randomUUID().toString().length + 1
                                ) // remove timestamp
                                .replace("\\A[0-9]+,".toRegex(), ""),
                        )
                    }
                    actualData = tmpData.toString()
                }
                assertEquals(expectedData, actualData)
            }
        assertFalse(outputFile.exists())
    }
}
