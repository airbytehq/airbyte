/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.util

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions

object ConfigTestUtils {
    fun getBaseConfig(formatConfig: JsonNode): JsonNode {
        return Jsons.deserialize(
            """{
  "gcs_bucket_name": "test-bucket-name",
  "gcs_bucket_path": "test_path",
  "gcs_bucket_region": "us-east-2",  "credential": {
    "credential_type": "HMAC_KEY",
    "hmac_key_access_id": "some_hmac_key",
    "hmac_key_secret": "some_key_secret"
  },  "format": $formatConfig}"""
        )
    }

    fun assertBaseConfig(gcsDestinationConfig: GcsDestinationConfig) {
        Assertions.assertEquals("test-bucket-name", gcsDestinationConfig.bucketName)
        Assertions.assertEquals("test_path", gcsDestinationConfig.bucketPath)
        Assertions.assertEquals("us-east-2", gcsDestinationConfig.bucketRegion)
    }
}
