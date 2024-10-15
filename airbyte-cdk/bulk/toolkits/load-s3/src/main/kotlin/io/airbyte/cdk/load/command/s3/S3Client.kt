/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
import aws.sdk.kotlin.services.s3.model.ListObjectsRequest
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.file.ObjectStorageClient
import io.airbyte.cdk.load.message.RemoteObject
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

class S3Object(
    override val key: String,
) : RemoteObject()

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3Client(
    private val client: aws.sdk.kotlin.services.s3.S3Client,
    private val bucketConfig: S3BucketConfiguration
) : ObjectStorageClient<S3Object> {
    override suspend fun list(prefix: String): List<S3Object> {
        val request = ListObjectsRequest {
            bucket = bucketConfig.s3BucketName
            this.prefix = prefix
        }
        return client.listObjects(request).contents?.mapNotNull {
            it.key?.let { key -> S3Object(key) }
        }
            ?: emptyList()
    }
}

@Factory
class S3ClientFactory(
    private val keyConfig: AWSAccessKeyConfigurationProvider,
    private val bucketConfig: S3BucketConfigurationProvider
) {

    @Singleton
    @Secondary
    fun make(): S3Client {
        val credentials = StaticCredentialsProvider {
            accessKeyId = keyConfig.awsAccessKeyConfiguration.accessKeyId
            secretAccessKey = keyConfig.awsAccessKeyConfiguration.secretAccessKey
        }

        val client =
            aws.sdk.kotlin.services.s3.S3Client {
                region = bucketConfig.s3BucketConfiguration.s3BucketRegion.name
                credentialsProvider = credentials
            }

        return S3Client(client, bucketConfig.s3BucketConfiguration)
    }
}
