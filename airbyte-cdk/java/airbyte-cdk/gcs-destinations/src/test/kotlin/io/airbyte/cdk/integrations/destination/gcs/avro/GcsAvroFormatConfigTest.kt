/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.avro

import com.amazonaws.services.s3.internal.Constants
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.util.ConfigTestUtils
import io.airbyte.cdk.integrations.destination.s3.avro.UploadAvroFormatConfig.Companion.parseCodecConfig
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.airbyte.commons.json.Jsons
import org.apache.avro.file.DataFileConstants
import org.apache.commons.lang3.reflect.FieldUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class GcsAvroFormatConfigTest {
    @Test
    fun testParseCodecConfigNull() {
        val nullConfigs: List<String> =
            Lists.newArrayList("{}", "{ \"codec\": \"no compression\" }")
        for (nullConfig in nullConfigs) {
            Assertions.assertEquals(
                DataFileConstants.NULL_CODEC,
                parseCodecConfig(Jsons.deserialize(nullConfig)).toString()
            )
        }
    }

    @Test
    fun testParseCodecConfigDeflate() {
        // default compression level 0
        val codecFactory1 = parseCodecConfig(Jsons.deserialize("{ \"codec\": \"deflate\" }"))
        Assertions.assertEquals("deflate-0", codecFactory1.toString())

        // compression level 5
        val codecFactory2 =
            parseCodecConfig(
                Jsons.deserialize("{ \"codec\": \"deflate\", \"compression_level\": 5 }")
            )
        Assertions.assertEquals("deflate-5", codecFactory2.toString())
    }

    @Test
    fun testParseCodecConfigBzip2() {
        val bzip2Config = Jsons.deserialize("{ \"codec\": \"bzip2\" }")
        val codecFactory = parseCodecConfig(bzip2Config)
        Assertions.assertEquals(DataFileConstants.BZIP2_CODEC, codecFactory.toString())
    }

    @Test
    fun testParseCodecConfigXz() {
        // default compression level 6
        val codecFactory1 = parseCodecConfig(Jsons.deserialize("{ \"codec\": \"xz\" }"))
        Assertions.assertEquals("xz-6", codecFactory1.toString())

        // compression level 7
        val codecFactory2 =
            parseCodecConfig(Jsons.deserialize("{ \"codec\": \"xz\", \"compression_level\": 7 }"))
        Assertions.assertEquals("xz-7", codecFactory2.toString())
    }

    @Test
    fun testParseCodecConfigZstandard() {
        // default compression level 3
        val codecFactory1 = parseCodecConfig(Jsons.deserialize("{ \"codec\": \"zstandard\" }"))
        // There is no way to verify the checksum; all relevant methods are private or protected...
        Assertions.assertEquals("zstandard[3]", codecFactory1.toString())

        // compression level 20
        val codecFactory2 =
            parseCodecConfig(
                Jsons.deserialize(
                    "{ \"codec\": \"zstandard\", \"compression_level\": 20, \"include_checksum\": true }"
                )
            )
        // There is no way to verify the checksum; all relevant methods are private or protected...
        Assertions.assertEquals("zstandard[20]", codecFactory2.toString())
    }

    @Test
    fun testParseCodecConfigSnappy() {
        val snappyConfig = Jsons.deserialize("{ \"codec\": \"snappy\" }")
        val codecFactory = parseCodecConfig(snappyConfig)
        Assertions.assertEquals(DataFileConstants.SNAPPY_CODEC, codecFactory.toString())
    }

    @Test
    fun testParseCodecConfigInvalid() {
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            val invalidConfig = Jsons.deserialize("{ \"codec\": \"bi-directional-bfs\" }")
            parseCodecConfig(invalidConfig)
        }
    }

    @Test
    @Throws(IllegalAccessException::class)
    fun testHandlePartSizeConfig() {
        val config =
            ConfigTestUtils.getBaseConfig(Jsons.deserialize("""{
  "format_type": "AVRO"
}"""))

        val gcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config)
        ConfigTestUtils.assertBaseConfig(gcsDestinationConfig)

        val formatConfig = gcsDestinationConfig.formatConfig!!
        Assertions.assertEquals("AVRO", formatConfig.format.name)
        // Assert that is set properly in config
        val streamTransferManager = create(gcsDestinationConfig.bucketName, "objectKey", null).get()

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
            ConfigTestUtils.getBaseConfig(Jsons.deserialize("""{
  "format_type": "AVRO"
}"""))

        val gcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config)
        ConfigTestUtils.assertBaseConfig(gcsDestinationConfig)

        val streamTransferManager = create(gcsDestinationConfig.bucketName, "objectKey", null).get()

        val partSizeBytes = FieldUtils.readField(streamTransferManager, "partSize", true) as Int
        Assertions.assertEquals(
            Constants.MB * StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB,
            partSizeBytes
        )
    }
}
