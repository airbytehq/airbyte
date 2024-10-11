/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command.s3

import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
import aws.sdk.kotlin.services.s3.model.ListObjectsRequest
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.ObjectStorageClient
import io.airbyte.cdk.load.message.RemoteObject
import java.nio.file.Path

class S3Object(
    override val key: String,
) : RemoteObject()

class S3Client(
    private val client: aws.sdk.kotlin.services.s3.S3Client,
    private val bucketConfig: S3BucketConfiguration
) : ObjectStorageClient<S3Object> {
    override suspend fun list(prefix: Path): List<S3Object> {
        val request = ListObjectsRequest {
            bucket = bucketConfig.s3BucketName
            this.prefix = prefix.toString()
        }
        return client.listObjects(request).contents?.mapNotNull {
            it.key?.let { key -> S3Object(key) }
        }
            ?: emptyList()
    }
}

fun <T> T.createS3Client(): S3Client where
T : AWSAccessKeyConfigurationProvider,
T : S3BucketConfigurationProvider {
    val credentials = StaticCredentialsProvider {
        accessKeyId = awsAccessKeyConfiguration.accessKeyId
        secretAccessKey = awsAccessKeyConfiguration.secretAccessKey
    }

    val client =
        aws.sdk.kotlin.services.s3.S3Client {
            region = s3BucketConfiguration.s3BucketRegion.name
            credentialsProvider = credentials
        }

    return S3Client(client, s3BucketConfiguration)
}
