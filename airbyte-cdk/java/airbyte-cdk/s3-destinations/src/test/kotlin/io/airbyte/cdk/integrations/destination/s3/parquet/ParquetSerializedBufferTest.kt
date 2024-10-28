/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.parquet

import com.amazonaws.util.IOUtils
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.util.JavaProcessRunner
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.io.FileOutputStream
import java.io.InputStream
import java.nio.file.Files
import java.util.UUID
import org.apache.avro.generic.GenericData
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.Path
import org.apache.parquet.avro.AvroReadSupport
import org.apache.parquet.hadoop.ParquetReader
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class ParquetSerializedBufferTest {

    companion object {
        private val MESSAGE_DATA: JsonNode =
            Jsons.jsonNode(
                mapOf(
                    "field1" to 10000,
                    "column2" to "string value",
                    "another field" to true,
                    "nested_column" to mapOf("array_column" to listOf(1, 2, 3)),
                    "string_array_column" to listOf("test_string", null),
                    "datetime_with_timezone" to "2022-05-12T15:35:44.192950Z",
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
                Field.of(
                    "string_array_column",
                    JsonSchemaType.builder(JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.ARRAY)
                        .withItems(JsonSchemaType.STRING)
                        .build(),
                ),
                Field.of("datetime_with_timezone", JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE),
            )
        private val catalog: ConfiguredAirbyteCatalog =
            CatalogHelpers.createConfiguredAirbyteCatalog(STREAM, null, FIELDS)

        @JvmStatic
        @BeforeAll
        internal fun setup() {
            DestinationConfig.initialize(Jsons.deserialize("{}"))
        }
    }

    @Test
    @Throws(Exception::class)
    internal fun testUncompressedParquetWriter() {
        val config =
            S3DestinationConfig.getS3DestinationConfig(
                Jsons.jsonNode(
                    mapOf(
                        "format" to
                            mapOf(
                                "format_type" to "parquet",
                            ),
                        "s3_bucket_name" to "test",
                        "s3_bucket_region" to "us-east-2",
                    ),
                ),
            )
        runTest(225L, 245L, config, getExpectedString())
    }

    @Test
    @Throws(Exception::class)
    internal fun testCompressedParquetWriter() {
        val config =
            S3DestinationConfig.getS3DestinationConfig(
                Jsons.jsonNode(
                    mapOf(
                        "format" to
                            mapOf(
                                "format_type" to "parquet",
                                "compression_codec" to "GZIP",
                            ),
                        "s3_bucket_name" to "test",
                        "s3_bucket_region" to "us-east-2",
                    ),
                ),
            )
        // TODO: Compressed parquet is the same size as uncompressed??
        runTest(225L, 245L, config, getExpectedString())
    }

    private fun resolveArchitecture(): String {
        return System.getProperty("os.name")
            .replace(
                ' ',
                '_',
            ) +
            "-" +
            System.getProperty("os.arch") +
            "-" +
            System.getProperty("sun.arch.data.model")
    }

    @Test
    @Throws(Exception::class)
    internal fun testLzoCompressedParquet() {
        val currentDir = System.getProperty("user.dir")
        val runtime = Runtime.getRuntime()
        val architecture = resolveArchitecture()
        if ((architecture == "Linux-amd64-64") || architecture == "Linux-x86_64-64") {
            JavaProcessRunner.runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get update")
            JavaProcessRunner.runProcess(
                currentDir,
                runtime,
                "/bin/sh",
                "-c",
                "apt-get install lzop liblzo2-2 liblzo2-dev -y",
            )
            runLzoParquetTest()
        } else if ((architecture == "Linux-aarch64-64") || architecture == "Linux-arm64-64") {
            JavaProcessRunner.runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get update")
            JavaProcessRunner.runProcess(
                currentDir,
                runtime,
                "/bin/sh",
                "-c",
                "apt-get install lzop liblzo2-2 liblzo2-dev " +
                    "wget curl unzip zip build-essential maven git -y",
            )
            JavaProcessRunner.runProcess(
                currentDir,
                runtime,
                "/bin/sh",
                "-c",
                "wget https://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz -P /usr/local/tmp",
            )
            JavaProcessRunner.runProcess(
                "/usr/local/tmp/",
                runtime,
                "/bin/sh",
                "-c",
                "tar xvfz lzo-2.10.tar.gz",
            )
            JavaProcessRunner.runProcess(
                "/usr/local/tmp/lzo-2.10/",
                runtime,
                "/bin/sh",
                "-c",
                "./configure --enable-shared --prefix /usr/local/lzo-2.10",
            )
            JavaProcessRunner.runProcess(
                "/usr/local/tmp/lzo-2.10/",
                runtime,
                "/bin/sh",
                "-c",
                "make && make install",
            )
            JavaProcessRunner.runProcess(
                currentDir,
                runtime,
                "/bin/sh",
                "-c",
                "git clone https://github.com/twitter/hadoop-lzo.git /usr/lib/hadoop/lib/hadoop-lzo/",
            )
            JavaProcessRunner.runProcess(
                currentDir,
                runtime,
                "/bin/sh",
                "-c",
                "curl -s https://get.sdkman.io | bash",
            )
            JavaProcessRunner.runProcess(
                currentDir,
                runtime,
                "/bin/bash",
                "-c",
                "source /root/.sdkman/bin/sdkman-init.sh;" +
                    " sdk install java 8.0.342-librca;" +
                    " sdk use java 8.0.342-librca;" +
                    " cd /usr/lib/hadoop/lib/hadoop-lzo/ " +
                    "&& C_INCLUDE_PATH=/usr/local/lzo-2.10/include " +
                    "LIBRARY_PATH=/usr/local/lzo-2.10/lib mvn clean package",
            )
            JavaProcessRunner.runProcess(
                currentDir,
                runtime,
                "/bin/sh",
                "-c",
                "find /usr/lib/hadoop/lib/hadoop-lzo/ -name '*libgplcompression*' -exec cp {} /usr/lib/ \\;",
            )
            runLzoParquetTest()
        }
    }

    @Throws(Exception::class)
    private fun runLzoParquetTest() {
        val config =
            S3DestinationConfig.getS3DestinationConfig(
                Jsons.jsonNode(
                    mapOf(
                        "format" to
                            mapOf(
                                "format_type" to "parquet",
                                "compression_codec" to "LZO",
                            ),
                        "s3_bucket_name" to "test",
                        "s3_bucket_region" to "us-east-2",
                    ),
                ),
            )
        runTest(225L, 245L, config, getExpectedString())
    }

    private fun getExpectedString(): String {
        return ("{\"_airbyte_ab_id\": \"<UUID>\", \"_airbyte_emitted_at\": \"<timestamp>\", " +
            "\"field1\": 10000.0, \"another_field\": true, " +
            "\"nested_column\": {\"_airbyte_additional_properties\": {\"array_column\": \"[1,2,3]\"}}, " +
            "\"column2\": \"string value\", " +
            "\"string_array_column\": [\"test_string\", null], " +
            "\"datetime_with_timezone\": 1652369744192000, " +
            "\"_airbyte_additional_properties\": null}")
    }

    @Throws(Exception::class)
    @Suppress("DEPRECATION")
    private fun runTest(
        minExpectedByte: Long,
        maxExpectedByte: Long,
        config: S3DestinationConfig,
        expectedData: String
    ) {
        val tempFile = Files.createTempFile(UUID.randomUUID().toString(), ".parquet").toFile()
        try {
            ParquetSerializedBuffer.createFunction(config).apply(streamPair, catalog).use { writer
                ->
                writer!!.accept(message)
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
                FileOutputStream(tempFile).use { outFile -> IOUtils.copy(`in`, outFile) }
                ParquetReader.builder(
                        AvroReadSupport<GenericData.Record>(),
                        Path(tempFile.absolutePath),
                    )
                    .withConf(Configuration())
                    .build()
                    .use { parquetReader ->
                        var record: GenericData.Record? = null
                        while ((parquetReader.read()?.also { record = it }) != null) {
                            record?.put("_airbyte_ab_id", "<UUID>")
                            record?.put("_airbyte_emitted_at", "<timestamp>")
                            val actualData: String = record.toString()
                            assertEquals(expectedData, actualData)
                        }
                    }
            }
        } finally {
            Files.deleteIfExists(tempFile.toPath())
        }
    }
}
