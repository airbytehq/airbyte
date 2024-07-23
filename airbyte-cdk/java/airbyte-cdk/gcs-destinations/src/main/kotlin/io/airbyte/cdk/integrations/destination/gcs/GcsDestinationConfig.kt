/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.client.builder.AwsClientBuilder
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsCredentialConfig
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsCredentialConfigs
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsCredentialType
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfig
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfigFactory.getUploadFormatConfig

/**
 * Currently we always reuse the S3 client for GCS. So the GCS config extends from the S3 config.
 * This may change in the future.
 */
class GcsDestinationConfig(
    bucketName: String,
    bucketPath: String,
    bucketRegion: String?,
    val gcsCredentialConfig: GcsCredentialConfig,
    formatConfig: UploadFormatConfig
) :
    S3DestinationConfig(
        GCS_ENDPOINT,
        bucketName,
        bucketPath,
        bucketRegion,
        S3DestinationConstants.DEFAULT_PATH_FORMAT,
        gcsCredentialConfig.s3CredentialConfig.orElseThrow(),
        formatConfig,
        null,
        null,
        false,
        S3StorageOperations.DEFAULT_UPLOAD_THREADS
    ) {
    override fun createS3Client(): AmazonS3 {
        when (gcsCredentialConfig.credentialType) {
            GcsCredentialType.HMAC_KEY -> {
                val hmacKeyCredential = gcsCredentialConfig as GcsHmacKeyCredentialConfig
                val awsCreds =
                    BasicAWSCredentials(
                        hmacKeyCredential.hmacKeyAccessId,
                        hmacKeyCredential.hmacKeySecret
                    )

                return AmazonS3ClientBuilder.standard()
                    .withEndpointConfiguration(
                        AwsClientBuilder.EndpointConfiguration(GCS_ENDPOINT, bucketRegion)
                    )
                    .withCredentials(AWSStaticCredentialsProvider(awsCreds))
                    .build()
            }
            else ->
                throw IllegalArgumentException(
                    "Unsupported credential type: " + gcsCredentialConfig.credentialType.name
                )
        }
    }

    companion object {
        private const val GCS_ENDPOINT = "https://storage.googleapis.com"

        @JvmStatic
        fun getGcsDestinationConfig(config: JsonNode): GcsDestinationConfig {
            return GcsDestinationConfig(
                config["gcs_bucket_name"].asText(),
                config["gcs_bucket_path"].asText(),
                config["gcs_bucket_region"].asText(),
                GcsCredentialConfigs.getCredentialConfig(config),
                getUploadFormatConfig(config)
            )
        }
    }
}
