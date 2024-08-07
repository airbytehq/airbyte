/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.avro

import com.amazonaws.services.s3.internal.Constants
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig.Companion.getS3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.StorageProvider
import io.airbyte.cdk.integrations.destination.s3.avro.UploadAvroFormatConfig.Companion.parseCodecConfig
import io.airbyte.cdk.integrations.destination.s3.util.ConfigTestUtils
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.commons.json.Jsons.deserialize
import org.apache.avro.file.DataFileConstants
import org.apache.commons.lang3.reflect.FieldUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class S3AvroFormatConfigTest {
    @Test
    fun testParseCodecConfigNull() {
        val nullConfigs: List<String> =
            Lists.newArrayList("{}", "{ \"codec\": \"no compression\" }")
        for (nullConfig in nullConfigs) {
            Assertions.assertEquals(
                DataFileConstants.NULL_CODEC,
                parseCodecConfig(deserialize(nullConfig)).toString()
            )
        }
    }

    @Test
    fun testParseCodecConfigDeflate() {
        // default compression level 0
        val codecFactory1 = parseCodecConfig(deserialize("{ \"codec\": \"deflate\" }"))
        Assertions.assertEquals("deflate-0", codecFactory1.toString())

        // compression level 5
        val codecFactory2 =
            parseCodecConfig(deserialize("{ \"codec\": \"deflate\", \"compression_level\": 5 }"))
        Assertions.assertEquals("deflate-5", codecFactory2.toString())
    }

    @Test
    fun testParseCodecConfigBzip2() {
        val bzip2Config = deserialize("{ \"codec\": \"bzip2\" }")
        val codecFactory = parseCodecConfig(bzip2Config)
        Assertions.assertEquals(DataFileConstants.BZIP2_CODEC, codecFactory.toString())
    }

    @Test
    fun testParseCodecConfigXz() {
        // default compression level 6
        val codecFactory1 = parseCodecConfig(deserialize("{ \"codec\": \"xz\" }"))
        Assertions.assertEquals("xz-6", codecFactory1.toString())

        // compression level 7
        val codecFactory2 =
            parseCodecConfig(deserialize("{ \"codec\": \"xz\", \"compression_level\": 7 }"))
        Assertions.assertEquals("xz-7", codecFactory2.toString())
    }

    @Test
    fun testParseCodecConfigZstandard() {
        // default compression level 3
        val codecFactory1 = parseCodecConfig(deserialize("{ \"codec\": \"zstandard\" }"))
        // There is no way to verify the checksum; all relevant methods are private or protected...
        Assertions.assertEquals("zstandard[3]", codecFactory1.toString())

        // compression level 20
        val codecFactory2 =
            parseCodecConfig(
                deserialize(
                    "{ \"codec\": \"zstandard\", \"compression_level\": 20, \"include_checksum\": true }"
                )
            )
        // There is no way to verify the checksum; all relevant methods are private or protected...
        Assertions.assertEquals("zstandard[20]", codecFactory2.toString())
    }

    @Test
    fun testParseCodecConfigSnappy() {
        val snappyConfig = deserialize("{ \"codec\": \"snappy\" }")
        val codecFactory = parseCodecConfig(snappyConfig)
        Assertions.assertEquals(DataFileConstants.SNAPPY_CODEC, codecFactory.toString())
    }

    @Test
    fun testParseCodecConfigInvalid() {
        try {
            val invalidConfig = deserialize("{ \"codec\": \"bi-directional-bfs\" }")
            parseCodecConfig(invalidConfig)
            Assertions.fail<Any>()
        } catch (e: IllegalArgumentException) {
            // expected
        }
    }

    @Test
    @Throws(IllegalAccessException::class)
    fun testHandlePartSizeConfig() {
        val config = ConfigTestUtils.getBaseConfig(deserialize("""{
  "format_type": "AVRO"
}"""))

        val s3DestinationConfig = getS3DestinationConfig(config!!, StorageProvider.AWS_S3)
        ConfigTestUtils.assertBaseConfig(s3DestinationConfig)

        val formatConfig = s3DestinationConfig.formatConfig
        Assertions.assertEquals("AVRO", formatConfig!!.format.name)
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
        val config = ConfigTestUtils.getBaseConfig(deserialize("""{
  "format_type": "AVRO"
}"""))

        val s3DestinationConfig = getS3DestinationConfig(config!!, StorageProvider.AWS_S3)
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
}
