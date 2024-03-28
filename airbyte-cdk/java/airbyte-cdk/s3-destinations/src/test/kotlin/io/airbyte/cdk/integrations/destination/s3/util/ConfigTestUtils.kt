/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig
import io.airbyte.commons.json.Jsons.deserialize
import org.junit.jupiter.api.Assertions

object ConfigTestUtils {
    fun getBaseConfig(formatConfig: JsonNode): JsonNode {
        return deserialize(
            """{
  "s3_endpoint": "some_test-endpoint",
  "s3_bucket_name": "test-bucket-name",
  "s3_bucket_path": "test_path",
  "s3_bucket_region": "us-east-2",
  "access_key_id": "some-test-key-id",
  "secret_access_key": "some-test-access-key",
  "format": $formatConfig}"""
        )
    }

    fun assertBaseConfig(s3DestinationConfig: S3DestinationConfig) {
        Assertions.assertEquals("some_test-endpoint", s3DestinationConfig.endpoint)
        Assertions.assertEquals("test-bucket-name", s3DestinationConfig.bucketName)
        Assertions.assertEquals("test_path", s3DestinationConfig.bucketPath)
        Assertions.assertEquals("us-east-2", s3DestinationConfig.bucketRegion)
        val credentialConfig = s3DestinationConfig.s3CredentialConfig as S3AccessKeyCredentialConfig
        Assertions.assertEquals("some-test-key-id", credentialConfig.accessKeyId)
        Assertions.assertEquals("some-test-access-key", credentialConfig.secretAccessKey)
    }
}
