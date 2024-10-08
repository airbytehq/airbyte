/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.csv

import com.amazonaws.services.s3.internal.Constants
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.util.ConfigTestUtils
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.Flattening.Companion.fromValue
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.airbyte.commons.json.Jsons
import org.apache.commons.lang3.reflect.FieldUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

// GcsCsvFormatConfig
class GcsCsvFormatConfigTest {
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
                Jsons.deserialize(
                    """{
  "format_type": "CSV",
  "flattening": "Root level flattening"
}"""
                )
            )

        val gcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config)
        ConfigTestUtils.assertBaseConfig(gcsDestinationConfig)

        val formatConfig = gcsDestinationConfig.formatConfig!!
        Assertions.assertEquals("CSV", formatConfig.format.name)
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
            ConfigTestUtils.getBaseConfig(
                Jsons.deserialize(
                    """{
  "format_type": "CSV",
  "flattening": "Root level flattening"
}"""
                )
            )

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
