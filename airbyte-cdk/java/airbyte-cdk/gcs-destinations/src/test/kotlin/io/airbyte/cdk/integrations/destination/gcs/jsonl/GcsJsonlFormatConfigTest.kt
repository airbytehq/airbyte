/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.jsonl

import com.amazonaws.services.s3.internal.Constants
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.util.ConfigTestUtils
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.airbyte.commons.json.Jsons
import org.apache.commons.lang3.reflect.FieldUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

// GcsJsonlFormatConfig
class GcsJsonlFormatConfigTest {
    @Test
    @Throws(IllegalAccessException::class)
    fun testHandlePartSizeConfig() {
        val config =
            ConfigTestUtils.getBaseConfig(Jsons.deserialize("""{
  "format_type": "JSONL"
}"""))

        val gcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config)
        ConfigTestUtils.assertBaseConfig(gcsDestinationConfig)

        val formatConfig = gcsDestinationConfig.formatConfig!!
        Assertions.assertEquals("JSONL", formatConfig.format.name)

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
  "format_type": "JSONL"
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
