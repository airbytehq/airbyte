/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.s3

import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
import aws.sdk.kotlin.services.s3.model.CompleteMultipartUploadRequest
import aws.sdk.kotlin.services.s3.model.CompletedMultipartUpload
import aws.sdk.kotlin.services.s3.model.CompletedPart
import aws.sdk.kotlin.services.s3.model.CopyObjectRequest
import aws.sdk.kotlin.services.s3.model.CreateMultipartUploadRequest
import aws.sdk.kotlin.services.s3.model.CreateMultipartUploadResponse
import aws.sdk.kotlin.services.s3.model.DeleteObjectRequest
import aws.sdk.kotlin.services.s3.model.GetObjectRequest
import aws.sdk.kotlin.services.s3.model.ListObjectsRequest
import aws.sdk.kotlin.services.s3.model.PutObjectRequest
import aws.sdk.kotlin.services.s3.model.UploadPartRequest
import aws.smithy.kotlin.runtime.content.ByteStream
import aws.smithy.kotlin.runtime.content.toInputStream
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStorageStreamingUploadWriter
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.InputStream
import kotlinx.coroutines.flow.flow

data class S3Object(override val key: String, override val bucketConfig: S3BucketConfiguration) :
    RemoteObject<S3BucketConfiguration> {
    val keyWithBucketName
        get() = "${bucketConfig.s3BucketName}/$key"
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3Client(
    private val client: aws.sdk.kotlin.services.s3.S3Client,
    val bucketConfig: S3BucketConfiguration,
    private val uploadConfig: ObjectStorageUploadConfiguration?,
) : ObjectStorageClient<S3Object, S3Client.S3MultipartUpload.Writer> {
    private val log = KotlinLogging.logger {}

    override suspend fun list(prefix: String) = flow {
        var request = ListObjectsRequest {
            bucket = bucketConfig.s3BucketName
            this.prefix = prefix
        }
        var lastKey: String? = null
        while (true) {
            val response = client.listObjects(request)
            response.contents?.forEach { obj ->
                lastKey = obj.key
                emit(S3Object(obj.key!!, bucketConfig))
            } // null contents => empty list, not error
            if (client.listObjects(request).isTruncated == false) {
                break
            }
            request = request.copy { marker = lastKey }
        }
    }

    override suspend fun move(remoteObject: S3Object, toKey: String): S3Object {
        val request = CopyObjectRequest {
            bucket = bucketConfig.s3BucketName
            this.key = toKey
            copySource = remoteObject.keyWithBucketName
        }
        client.copyObject(request)
        delete(remoteObject)
        return S3Object(toKey, bucketConfig)
    }

    override suspend fun <R> get(key: String, block: (InputStream) -> R): R {
        val request = GetObjectRequest {
            bucket = bucketConfig.s3BucketName
            this.key = key
        }
        return client.getObject(request) {
            it.body?.toInputStream()?.use(block)
                ?: throw IllegalStateException(
                    "S3 object body is null (this indicates a failure, not an empty object"
                )
        }
    }

    override suspend fun put(key: String, bytes: ByteArray): S3Object {
        val request = PutObjectRequest {
            bucket = bucketConfig.s3BucketName
            this.key = key
            body = ByteStream.fromBytes(bytes)
        }
        client.putObject(request)
        return S3Object(key, bucketConfig)
    }

    override suspend fun delete(remoteObject: S3Object) {
        val request = DeleteObjectRequest {
            bucket = remoteObject.bucketConfig.s3BucketName
            this.key = remoteObject.key
        }
        client.deleteObject(request)
    }

    override suspend fun streamingUpload(
        key: String,
        collector: suspend S3MultipartUpload.Writer.() -> Unit
    ): S3Object {
        val request = CreateMultipartUploadRequest {
            this.bucket = bucketConfig.s3BucketName
            this.key = key
        }
        val response = client.createMultipartUpload(request)
        S3MultipartUpload(response).upload(collector)
        return S3Object(key, bucketConfig)
    }

    inner class S3MultipartUpload(private val response: CreateMultipartUploadResponse) {
        private val uploadedParts = mutableListOf<CompletedPart>()
        private var inputBuffer = ByteArrayOutputStream()
        private val partSize =
            uploadConfig?.streamingUploadPartSize
                ?: throw IllegalStateException("Streaming upload part size is not configured")

        suspend fun upload(collector: suspend S3MultipartUpload.Writer.() -> Unit) {
            log.info {
                "Starting multipart upload to ${response.bucket}/${response.key} (${response.uploadId}"
            }
            collector.invoke(Writer())
            complete()
        }

        inner class Writer : ObjectStorageStreamingUploadWriter {
            override suspend fun write(bytes: ByteArray) {
                inputBuffer.write(bytes)
                if (inputBuffer.size() >= partSize) {
                    uploadPart()
                }
            }

            override suspend fun write(string: String) {
                write(string.toByteArray(Charsets.UTF_8))
            }
        }

        private suspend fun uploadPart() {
            val partNumber = uploadedParts.size + 1
            val request = UploadPartRequest {
                uploadId = response.uploadId
                bucket = response.bucket
                key = response.key
                body = ByteStream.fromBytes(inputBuffer.toByteArray())
                this.partNumber = partNumber
            }
            val uploadResponse = client.uploadPart(request)
            uploadedParts.add(
                CompletedPart {
                    this.partNumber = partNumber
                    this.eTag = uploadResponse.eTag
                }
            )
            inputBuffer.reset()
        }

        private suspend fun complete() {
            if (inputBuffer.size() > 0) {
                uploadPart()
            }
            log.info {
                "Completing multipart upload to ${response.bucket}/${response.key} (${response.uploadId}"
            }
            val request = CompleteMultipartUploadRequest {
                uploadId = response.uploadId
                bucket = response.bucket
                key = response.key
                this.multipartUpload = CompletedMultipartUpload { parts = uploadedParts }
            }
            client.completeMultipartUpload(request)
        }
    }
}

@Factory
class S3ClientFactory(
    private val keyConfig: AWSAccessKeyConfigurationProvider,
    private val bucketConfig: S3BucketConfigurationProvider,
    private val uploadConifg: ObjectStorageUploadConfigurationProvider? = null,
) {
    companion object {
        fun <T> make(config: T) where
        T : S3BucketConfigurationProvider,
        T : AWSAccessKeyConfigurationProvider,
        T : ObjectStorageUploadConfigurationProvider =
            S3ClientFactory(config, config, config).make()
    }

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

        return S3Client(
            client,
            bucketConfig.s3BucketConfiguration,
            uploadConifg?.objectStorageUploadConfiguration
        )
    }
}
