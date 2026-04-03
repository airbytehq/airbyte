/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.client.builder.AwsClientBuilder
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.fasterxml.jackson.databind.JsonNode
import com.google.cloud.storage.Storage
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsCredentialConfig
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsCredentialConfigs
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsCredentialType
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsServiceAccountCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfig
import io.airbyte.cdk.integrations.destination.s3.UploadFormatConfigFactory.getUploadFormatConfig

/**
 * GCS destination configuration that supports both HMAC key authentication (via S3-compatible API)
 * and Service Account authentication (via native GCS client).
 *
 * For HMAC key authentication, this class extends S3DestinationConfig and uses the S3 client. For
 * Service Account authentication, use the companion object methods to get the native GCS client.
 */
class GcsDestinationConfig
private constructor(
    bucketName: String,
    bucketPath: String,
    bucketRegion: String?,
    val gcsCredentialConfig: GcsCredentialConfig,
    formatConfig: UploadFormatConfig,
    private val useNativeClient: Boolean
) :
    S3DestinationConfig(
        GCS_ENDPOINT,
        bucketName,
        bucketPath,
        bucketRegion,
        S3DestinationConstants.DEFAULT_PATH_FORMAT,
        if (useNativeClient) null else gcsCredentialConfig.s3CredentialConfig.orElseThrow(),
        formatConfig,
        null,
        null,
        false,
        S3StorageOperations.DEFAULT_UPLOAD_THREADS
    ) {

    fun isUsingNativeClient(): Boolean = useNativeClient

    fun getNativeGcsClient(): Storage {
        if (!useNativeClient) {
            throw IllegalStateException(
                "Native GCS client is only available for Service Account authentication"
            )
        }
        val serviceAccountCredential = gcsCredentialConfig as GcsServiceAccountCredentialConfig
        return GcsNativeStorageOperations.createStorageClient(
            serviceAccountCredential.serviceAccountJson
        )
    }

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
            GcsCredentialType.SERVICE_ACCOUNT ->
                throw IllegalStateException(
                    "S3 client is not available for Service Account authentication. Use getNativeGcsClient() instead."
                )
        }
    }

    companion object {
        const val GCS_ENDPOINT = "https://storage.googleapis.com"

        @JvmStatic
        fun getGcsDestinationConfig(config: JsonNode): GcsDestinationConfig {
            val credentialConfig = GcsCredentialConfigs.getCredentialConfig(config)
            val useNativeClient =
                credentialConfig.credentialType == GcsCredentialType.SERVICE_ACCOUNT

            return GcsDestinationConfig(
                config["gcs_bucket_name"].asText(),
                config["gcs_bucket_path"].asText(),
                config["gcs_bucket_region"].asText(),
                credentialConfig,
                getUploadFormatConfig(config),
                useNativeClient
            )
        }
    }
}
