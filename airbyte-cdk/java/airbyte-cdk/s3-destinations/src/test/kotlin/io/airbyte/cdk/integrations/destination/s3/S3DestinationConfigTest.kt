/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig.Companion.create
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig.Companion.getS3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig
import io.airbyte.commons.json.Jsons.deserialize
import org.assertj.core.api.AssertionsForClassTypes
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class S3DestinationConfigTest {
    @Test
    fun testCreateFromExistingConfig() {
        Assertions.assertEquals(CONFIG, create(CONFIG).get())
    }

    @Test
    fun testCreateAndModify() {
        val newBucketName = "new-bucket"
        val newBucketPath = "new-path"
        val newBucketRegion = "new-region"
        val newEndpoint = "new-endpoint"
        val newKey = "new-key"
        val newSecret = "new-secret"

        val modifiedConfig =
            create(CONFIG)
                .withBucketName(newBucketName)
                .withBucketPath(newBucketPath)
                .withBucketRegion(newBucketRegion)
                .withEndpoint(newEndpoint)
                .withAccessKeyCredential(newKey, newSecret)
                .get()

        Assertions.assertNotEquals(CONFIG, modifiedConfig)
        Assertions.assertEquals(newBucketName, modifiedConfig.bucketName)
        Assertions.assertEquals(newBucketPath, modifiedConfig.bucketPath)
        Assertions.assertEquals(newBucketRegion, modifiedConfig.bucketRegion)

        val credentialConfig = modifiedConfig.s3CredentialConfig as S3AccessKeyCredentialConfig
        Assertions.assertEquals(newKey, credentialConfig.accessKeyId)
        Assertions.assertEquals(newSecret, credentialConfig.secretAccessKey)
    }

    @Test
    fun testGetS3DestinationConfigAWS_S3Provider() {
        val s3config =
            deserialize(
                """{
  "s3_bucket_name": "paste-bucket-name-here",
  "s3_bucket_path": "integration-test",
  "s3_bucket_region": "paste-bucket-region-here",
  "access_key_id": "paste-access-key-id-here",
  "secret_access_key": "paste-secret-access-key-here"
}"""
            )

        val result = getS3DestinationConfig(s3config, StorageProvider.AWS_S3)

        AssertionsForClassTypes.assertThat(result.endpoint).isEmpty()
        AssertionsForClassTypes.assertThat(result.bucketName).isEqualTo("paste-bucket-name-here")
        AssertionsForClassTypes.assertThat(result.bucketPath).isEqualTo("integration-test")
        AssertionsForClassTypes.assertThat(result.bucketRegion)
            .isEqualTo("paste-bucket-region-here")
        AssertionsForClassTypes.assertThat(result.pathFormat)
            .isEqualTo("\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_")
        val awsCredentials = result.s3CredentialConfig!!.s3CredentialsProvider.credentials
        AssertionsForClassTypes.assertThat(awsCredentials.awsAccessKeyId)
            .isEqualTo("paste-access-key-id-here")
        AssertionsForClassTypes.assertThat(awsCredentials.awsSecretKey)
            .isEqualTo("paste-secret-access-key-here")
        AssertionsForClassTypes.assertThat(result.isCheckIntegrity).isEqualTo(true)
    }

    @Test
    fun testGetS3DestinationConfigCF_R2Provider() {
        val s3config =
            deserialize(
                """{
  "s3_bucket_name": "paste-bucket-name-here",
  "s3_bucket_path": "integration-test",
  "account_id": "paster-account-id-here",
  "access_key_id": "paste-access-key-id-here",
  "secret_access_key": "paste-secret-access-key-here"
}
"""
            )

        val result = getS3DestinationConfig(s3config, StorageProvider.CF_R2)

        AssertionsForClassTypes.assertThat(result.endpoint)
            .isEqualTo("https://paster-account-id-here.r2.cloudflarestorage.com")
        AssertionsForClassTypes.assertThat(result.bucketName).isEqualTo("paste-bucket-name-here")
        AssertionsForClassTypes.assertThat(result.bucketPath).isEqualTo("integration-test")
        AssertionsForClassTypes.assertThat(result.bucketRegion).isNull()
        AssertionsForClassTypes.assertThat(result.pathFormat)
            .isEqualTo("\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_")
        val awsCredentials = result.s3CredentialConfig!!.s3CredentialsProvider.credentials
        AssertionsForClassTypes.assertThat(awsCredentials.awsAccessKeyId)
            .isEqualTo("paste-access-key-id-here")
        AssertionsForClassTypes.assertThat(awsCredentials.awsSecretKey)
            .isEqualTo("paste-secret-access-key-here")
        AssertionsForClassTypes.assertThat(result.isCheckIntegrity).isEqualTo(false)
    }

    companion object {
        private val CONFIG =
            create("test-bucket", "test-path", "test-region")
                .withEndpoint("test-endpoint")
                .withPathFormat("\${STREAM_NAME}/\${NAMESPACE}")
                .withAccessKeyCredential("test-key", "test-secret")
                .get()
    }
}
