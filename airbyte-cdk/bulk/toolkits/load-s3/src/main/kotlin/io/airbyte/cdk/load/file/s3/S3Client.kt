/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.s3

import aws.sdk.kotlin.runtime.auth.credentials.AssumeRoleParameters
import aws.sdk.kotlin.runtime.auth.credentials.DefaultChainCredentialsProvider
import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
import aws.sdk.kotlin.runtime.auth.credentials.StsAssumeRoleCredentialsProvider
import aws.sdk.kotlin.services.s3.model.CopyObjectRequest
import aws.sdk.kotlin.services.s3.model.CreateMultipartUploadRequest
import aws.sdk.kotlin.services.s3.model.DeleteObjectRequest
import aws.sdk.kotlin.services.s3.model.GetObjectRequest
import aws.sdk.kotlin.services.s3.model.HeadObjectRequest
import aws.sdk.kotlin.services.s3.model.ListObjectsRequest
import aws.sdk.kotlin.services.s3.model.PutObjectRequest
import aws.smithy.kotlin.runtime.auth.awscredentials.CredentialsProvider
import aws.smithy.kotlin.runtime.content.ByteStream
import aws.smithy.kotlin.runtime.content.toInputStream
import aws.smithy.kotlin.runtime.http.engine.crt.CrtHttpEngine
import aws.smithy.kotlin.runtime.net.url.Url
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.OutputStream
import kotlinx.coroutines.flow.flow

data class S3Object(override val key: String, override val storageConfig: S3BucketConfiguration) :
    RemoteObject<S3BucketConfiguration> {
    val keyWithBucketName
        get() = "${storageConfig.s3BucketName}/$key"
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3Client(
    private val client: aws.sdk.kotlin.services.s3.S3Client,
    val bucketConfig: S3BucketConfiguration,
    private val uploadConfig: ObjectStorageUploadConfiguration?,
) : ObjectStorageClient<S3Object> {
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

    override suspend fun move(key: String, toKey: String): S3Object {
        return move(S3Object(key, bucketConfig), toKey)
    }

    override suspend fun <R> get(key: String, block: (InputStream) -> R): R {
        val request = GetObjectRequest {
            bucket = bucketConfig.s3BucketName
            this.key = key
        }
        return client.getObject(request) {
            val inputStream =
                it.body?.toInputStream()
                    ?: throw IllegalStateException(
                        "S3 object body is null (this indicates a failure, not an empty object)"
                    )
            block(inputStream)
        }
    }

    override suspend fun getMetadata(key: String): Map<String, String> {
        val request = HeadObjectRequest {
            bucket = bucketConfig.s3BucketName
            this.key = key
        }
        return client.headObject(request).metadata ?: emptyMap()
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
            bucket = remoteObject.storageConfig.s3BucketName
            this.key = remoteObject.key
        }
        client.deleteObject(request)
    }

    override suspend fun delete(key: String) {
        delete(S3Object(key, bucketConfig))
    }

    override suspend fun <U : OutputStream> streamingUpload(
        key: String,
        metadata: Map<String, String>,
        streamProcessor: StreamProcessor<U>?,
        block: suspend (OutputStream) -> Unit
    ): S3Object {
        return streamingUploadInner(key, metadata, streamProcessor, block)
    }

    private suspend fun <U : OutputStream> streamingUploadInner(
        key: String,
        metadata: Map<String, String>,
        streamProcessor: StreamProcessor<U>?,
        block: suspend (OutputStream) -> Unit
    ): S3Object {
        val request = CreateMultipartUploadRequest {
            this.bucket = bucketConfig.s3BucketName
            this.key = key
            this.metadata = metadata
        }
        val response = client.createMultipartUpload(request)
        val upload =
            S3MultipartUpload(
                client,
                response,
                ByteArrayOutputStream(),
                streamProcessor ?: NoopProcessor,
                uploadConfig
            )
        upload.runUsing(block)
        return S3Object(key, bucketConfig)
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<S3Object> {
        val request = CreateMultipartUploadRequest {
            this.bucket = bucketConfig.s3BucketName
            this.key = key
            this.metadata = metadata
        }
        val response = client.createMultipartUpload(request)

        log.info { "Starting multipart upload for $key (uploadId=${response.uploadId})" }

        return S3StreamingUpload(client, bucketConfig, response)
    }
}

/**
 * The assume role parameters (access key, secret key, external ID) are required if
 * [keyConfig.awsAccessKeyConfiguration.accessKeyId] is null and
 * [arnRole.awsArnRoleConfiguration.roleArn] is not null. (i.e. if the user is actually trying to do
 * the assume role flow, then we need platform to provide the relevant parameters.)
 */
@Factory
class S3ClientFactory(
    private val arnRole: AWSArnRoleConfigurationProvider,
    private val keyConfig: AWSAccessKeyConfigurationProvider,
    private val bucketConfig: S3BucketConfigurationProvider,
    private val uploadConfig: ObjectStorageUploadConfigurationProvider? = null,
    @Value("\${airbyte.destination.s3.assume-role.access-key}") val assumeRoleAccessKey: String?,
    @Value("\${airbyte.destination.s3.assume-role.secret-key}") val assumeRoleSecretKey: String?,
    @Value("\${airbyte.destination.s3.assume-role.external-id}") val assumeRoleExternalId: String?,
) {
    companion object {
        const val AIRBYTE_STS_SESSION_NAME = "airbyte-sts-session"

        fun <T> make(
            config: T,
            accessKey: String?,
            secretKey: String?,
            externalId: String?,
        ) where
        T : S3BucketConfigurationProvider,
        T : AWSAccessKeyConfigurationProvider,
        T : AWSArnRoleConfigurationProvider,
        T : ObjectStorageUploadConfigurationProvider =
            S3ClientFactory(config, config, config, config, accessKey, secretKey, externalId).make()
    }

    @Singleton
    @Secondary
    fun make(): S3Client {
        val credsProvider: CredentialsProvider =
            if (keyConfig.awsAccessKeyConfiguration.accessKeyId != null) {
                StaticCredentialsProvider {
                    accessKeyId = keyConfig.awsAccessKeyConfiguration.accessKeyId
                    secretAccessKey = keyConfig.awsAccessKeyConfiguration.secretAccessKey
                }
            } else if (arnRole.awsArnRoleConfiguration.roleArn != null) {
                // The Platform is expected to inject via credentials if ROLE_ARN is present.
                val assumeRoleParams =
                    AssumeRoleParameters(
                        roleArn = arnRole.awsArnRoleConfiguration.roleArn!!,
                        roleSessionName = AIRBYTE_STS_SESSION_NAME,
                        externalId = assumeRoleExternalId!!
                    )
                val creds = StaticCredentialsProvider {
                    accessKeyId = assumeRoleAccessKey!!
                    secretAccessKey = assumeRoleSecretKey!!
                }
                StsAssumeRoleCredentialsProvider(
                    bootstrapCredentialsProvider = creds,
                    assumeRoleParameters = assumeRoleParams
                )
            } else {
                DefaultChainCredentialsProvider()
            }

        val s3SdkClient =
            aws.sdk.kotlin.services.s3.S3Client {
                region = bucketConfig.s3BucketConfiguration.s3BucketRegion.name
                credentialsProvider = credsProvider
                endpointUrl =
                    bucketConfig.s3BucketConfiguration.s3Endpoint?.let {
                        if (it.isNotBlank()) {
                            Url.parse(it)
                        } else null
                    }

                // Fix for connection reset issue:
                // https://github.com/awslabs/aws-sdk-kotlin/issues/1214#issuecomment-2464831817
                httpClient(CrtHttpEngine)
            }

        return S3Client(
            s3SdkClient,
            bucketConfig.s3BucketConfiguration,
            uploadConfig?.objectStorageUploadConfiguration
        )
    }
}
