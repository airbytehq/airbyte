/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import com.amazonaws.services.s3.internal.Constants
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig.Companion.getS3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.ConfigTestUtils
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.Flattening.Companion.fromValue
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.commons.json.Jsons.deserialize
import org.apache.commons.lang3.reflect.FieldUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

// S3CsvFormatConfig
class S3CsvFormatConfigTest {
    @Test // Flattening enums can be created from value string
    fun testFlatteningCreationFromString() {
        Assertions.assertEquals(Flattening.NO, fromValue("no flattening"))
        Assertions.assertEquals(Flattening.ROOT_LEVEL, fromValue("root level flattening"))
        try {
            fromValue("invalid flattening value")
        } catch (e: Exception) {
            Assertions.assertTrue(e is IllegalArgumentException)
        }
    }

    @Test
    @Throws(IllegalAccessException::class)
    fun testHandlePartSizeConfig() {
        val config =
            ConfigTestUtils.getBaseConfig(
                deserialize(
                    """{
  "format_type": "CSV",
  "flattening": "Root level flattening"
}"""
                )
            )

        val s3DestinationConfig = getS3DestinationConfig(config!!)
        ConfigTestUtils.assertBaseConfig(s3DestinationConfig)

        val formatConfig = s3DestinationConfig.formatConfig
        Assertions.assertEquals("CSV", formatConfig!!.format.name)
        // Assert that is set properly in config
        val streamTransferManager =
            StreamTransferManagerFactory.create(s3DestinationConfig.bucketName, "objectKey", null)
                .get()

        val partSizeBytes = FieldUtils.readField(streamTransferManager, "partSize", true) as Int
        Assertions.assertEquals(
            Constants.MB * StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB,
            partSizeBytes
        )
    }

    @Test
    @Throws(IllegalAccessException::class)
    fun testHandleAbsenceOfPartSizeConfig() {
        val config =
            ConfigTestUtils.getBaseConfig(
                deserialize(
                    """{
  "format_type": "CSV",
  "flattening": "Root level flattening"
}"""
                )
            )

        val s3DestinationConfig = getS3DestinationConfig(config!!)
        ConfigTestUtils.assertBaseConfig(s3DestinationConfig)

        val streamTransferManager =
            StreamTransferManagerFactory.create(s3DestinationConfig.bucketName, "objectKey", null)
                .get()

        val partSizeBytes = FieldUtils.readField(streamTransferManager, "partSize", true) as Int
        Assertions.assertEquals(
            Constants.MB * StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB,
            partSizeBytes
        )
    }

    @Test
    fun testGzipCompressionConfig() {
        // without gzip compression config
        val configWithoutGzipCompression =
            ConfigTestUtils.getBaseConfig(deserialize("""{
  "format_type": "CSV"
}"""))
        val s3ConfigWithoutGzipCompression = getS3DestinationConfig(configWithoutGzipCompression!!)
        Assertions.assertEquals(
            S3DestinationConstants.DEFAULT_COMPRESSION_TYPE,
            (s3ConfigWithoutGzipCompression.formatConfig as UploadCsvFormatConfig?)!!
                .compressionType
        )

        // with gzip compression config
        val configWithGzipCompression =
            ConfigTestUtils.getBaseConfig(
                deserialize("""{
  "format_type": "CSV",
  "gzip_compression": false
}""")
            )
        val gcsConfigWithGzipCompression = getS3DestinationConfig(configWithGzipCompression!!)
        Assertions.assertEquals(
            CompressionType.GZIP,
            (gcsConfigWithGzipCompression.formatConfig as UploadCsvFormatConfig?)!!.compressionType
        )
    }
}
