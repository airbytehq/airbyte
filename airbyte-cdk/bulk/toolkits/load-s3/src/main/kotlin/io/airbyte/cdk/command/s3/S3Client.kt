/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command.s3

import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
import aws.sdk.kotlin.services.s3.model.CompleteMultipartUploadRequest
import aws.sdk.kotlin.services.s3.model.CompletedMultipartUpload
import aws.sdk.kotlin.services.s3.model.CompletedPart
import aws.sdk.kotlin.services.s3.model.CopyObjectRequest
import aws.sdk.kotlin.services.s3.model.CreateMultipartUploadRequest
import aws.sdk.kotlin.services.s3.model.CreateMultipartUploadResponse
import aws.sdk.kotlin.services.s3.model.DeleteObjectRequest
import aws.sdk.kotlin.services.s3.model.ListObjectsRequest
import aws.sdk.kotlin.services.s3.model.UploadPartRequest
import aws.smithy.kotlin.runtime.content.ByteStream
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.ObjectStorageClient
import io.airbyte.cdk.load.file.RemoteObject
import io.airbyte.cdk.load.file.StreamingUpload
import io.airbyte.cdk.load.state.MemoryManager
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream

data class S3Object(
    override val key: String,
    override val bucketConfig: S3BucketConfiguration
) : RemoteObject<S3BucketConfiguration>

class S3Client(
    private val client: aws.sdk.kotlin.services.s3.S3Client,
    private val bucketConfig: S3BucketConfiguration,
    private val memoryManager: MemoryManager
) : ObjectStorageClient<S3Object> {
    companion object {
        private const val PART_SIZE = 5L * 1024 * 1024 // 5 MB
    }

    override suspend fun delete(key: String) {
        val request = DeleteObjectRequest {
            bucket = bucketConfig.s3BucketName
            this.key = key
        }
        client.deleteObject(request)
    }

    override suspend fun list(prefix: String): List<S3Object> {
        val request = ListObjectsRequest {
            bucket = bucketConfig.s3BucketName
            this.prefix = prefix
        }
        return client.listObjects(request).contents?.mapNotNull {
            it.key?.let { key -> S3Object(key, bucketConfig) }
        }
            ?: emptyList()
    }

    override suspend fun move(remoteObject: S3Object, toKey: String) {
        val request = CopyObjectRequest {
            bucket = bucketConfig.s3BucketName
            copySource = "${remoteObject.bucketConfig.s3BucketName}/${remoteObject.key}"
            key = toKey
        }
        client.copyObject(request)
        delete(remoteObject.key)
    }

    override suspend fun streamingUpload(
        key: String,
        collector: suspend () -> ByteArray?
    ): S3MultipartUpload {
        val request = CreateMultipartUploadRequest {
            this.bucket = bucketConfig.s3BucketName
            this.key = key
        }
        val response = client.createMultipartUpload(request)
        return S3MultipartUpload(response, PART_SIZE, collector)
    }

    inner class S3MultipartUpload(
        private val response: CreateMultipartUploadResponse,
        private val partSize: Long,
        private val collector: suspend () -> ByteArray?,
        private val mapper: List<suspend (ByteArray) -> ByteArray> = emptyList()
    ): StreamingUpload<S3Object> {
        private val uploadedParts = mutableListOf<CompletedPart>()
        private var inputBuffer = ByteArrayOutputStream()

        override suspend fun mapPart(f: suspend (ByteArray) -> ByteArray): StreamingUpload<S3Object> {
            return S3MultipartUpload(response, partSize, collector, mapper + f)
        }

        override suspend fun upload(): S3Object {
            while (true) {
                val data = collector() ?: break
                inputBuffer.write(data)
                if (inputBuffer.size() >= partSize) {
                    uploadPart()
                }
            }
            complete()
            return S3Object(response.key!!, bucketConfig)
        }

        private suspend fun uploadPart() {
            val partNumber = uploadedParts.size + 1
            val mapped = mapper.fold(inputBuffer.toByteArray()) { acc, f -> f(acc) }
            val request = UploadPartRequest {
                uploadId = response.uploadId
                bucket = response.bucket
                key = response.key
                body = ByteStream.fromBytes(mapped)
                this.partNumber = partNumber
            }
            val uploadResponse = client.uploadPart(request)
            uploadedParts.add(CompletedPart {
                this.partNumber = partNumber
                this.eTag = uploadResponse.eTag
            })
            inputBuffer.reset()
        }

        private suspend fun complete() {
            if (inputBuffer.size() > 0) {
                uploadPart()
            }
            val request = CompleteMultipartUploadRequest {
                uploadId = response.uploadId
                bucket = response.bucket
                key = response.key
                this.multipartUpload = CompletedMultipartUpload {
                    parts = uploadedParts
                }
            }
            client.completeMultipartUpload(request)
        }
    }
}

@Factory
class S3CientFactory(
    private val memoryManager: MemoryManager,
    private val keyConfig: AWSAccessKeyConfigurationProvider,
    private val bucketConfig: S3BucketConfigurationProvider
) {

    @Singleton
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

        return S3Client(client, bucketConfig.s3BucketConfiguration, memoryManager)
    }
}
