/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.jsonl

import com.amazonaws.services.s3.internal.Constants
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig.Companion.getS3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.util.ConfigTestUtils
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.Flattening.Companion.fromValue
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.commons.json.Jsons.deserialize
import org.apache.commons.lang3.reflect.FieldUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

// S3JsonlFormatConfig
class S3JsonlFormatConfigTest {
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
        val config = ConfigTestUtils.getBaseConfig(deserialize("""{
  "format_type": "JSONL"
}"""))

        val s3DestinationConfig = getS3DestinationConfig(config!!)
        ConfigTestUtils.assertBaseConfig(s3DestinationConfig)

        val formatConfig = s3DestinationConfig.formatConfig
        Assertions.assertEquals("JSONL", formatConfig!!.format.name)

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
  "format_type": "JSONL"
}"""))

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
}
