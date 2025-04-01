/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.s3

import com.amazonaws.ClientConfiguration
import com.amazonaws.Protocol
import com.amazonaws.auth.AWSCredentials
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.auth.STSAssumeRoleSessionCredentialsProvider
import com.amazonaws.client.builder.AwsClientBuilder
import com.amazonaws.endpointdiscovery.DaemonThreadFactory
import com.amazonaws.regions.Regions
import com.amazonaws.retry.RetryMode
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.amazonaws.services.s3.model.CompleteMultipartUploadRequest
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult
import com.amazonaws.services.s3.model.ObjectMetadata
import com.amazonaws.services.s3.model.PartETag
import com.amazonaws.services.s3.model.UploadPartRequest
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClient
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.file.s3.S3ClientFactory.Companion.AIRBYTE_STS_SESSION_NAME
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.InputStream
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.asFlow
import org.apache.mina.util.ConcurrentHashSet

/**
 * A Java S3 SDK that is scheduled to be deprecated at the end of 2025. It was used by the old CDK
 * and lacks a bug that (sometimes) prevents the new Kotlin SDK from running with max concurrency.
 * (See https://github.com/awslabs/aws-sdk-kotlin/issues/1214#issuecomment-2464831817.)
 *
 * This can be enabled by injecting [io.airbyte.cdk.load.command.s3.S3ClientConfigurationProvider]
 * with [io.airbyte.cdk.load.command.s3.S3ClientConfiguration.useLegacyJavaClient] set to `true`.
 *
 * Currently this exists only to facilitate performance testing, but it may be needed as a fallback
 * if the new SDK cannot meet performance requirements.
 */
class S3LegacyJavaClient(val amazonS3: AmazonS3, val bucket: S3BucketConfiguration) : S3Client {
    override suspend fun list(prefix: String): Flow<S3Object> {
        return amazonS3
            .listObjectsV2(bucket.s3BucketName, prefix)
            .objectSummaries
            .map { S3Object(it.key, bucket) }
            .asFlow()
    }

    override suspend fun move(remoteObject: S3Object, toKey: String): S3Object {
        amazonS3.copyObject(bucket.s3BucketName, remoteObject.key, bucket.s3BucketName, toKey)
        amazonS3.deleteObject(bucket.s3BucketName, remoteObject.key)

        return S3Object(toKey, bucket)
    }

    override suspend fun move(key: String, toKey: String): S3Object {
        return move(S3Object(key, bucket), toKey)
    }

    override suspend fun <U> get(key: String, block: (InputStream) -> U): U {
        val obj = amazonS3.getObject(bucket.s3BucketName, key)
        return obj.objectContent.use(block)
    }

    override suspend fun getMetadata(key: String): Map<String, String> {
        val obj = amazonS3.getObjectMetadata(bucket.s3BucketName, key)
        return obj.userMetadata
    }

    override suspend fun put(key: String, bytes: ByteArray): S3Object {
        amazonS3.putObject(bucket.s3BucketName, key, bytes.inputStream(), null)
        return S3Object(key, bucket)
    }

    override suspend fun delete(remoteObject: S3Object) {
        amazonS3.deleteObject(bucket.s3BucketName, remoteObject.key)
    }

    override suspend fun delete(key: String) {
        amazonS3.deleteObject(bucket.s3BucketName, key)
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<S3Object> {
        val request =
            InitiateMultipartUploadRequest(bucket.s3BucketName, key)
                .withObjectMetadata(ObjectMetadata().also { it.userMetadata = metadata })
        val response = amazonS3.initiateMultipartUpload(request)
        return S3LegacyJavaStreamingUpload(amazonS3, bucket, response)
    }
}

class S3LegacyJavaStreamingUpload(
    private val amazonS3: AmazonS3,
    private val bucket: S3BucketConfiguration,
    private val response: InitiateMultipartUploadResult
) : StreamingUpload<S3Object> {
    private val log = KotlinLogging.logger {}

    private val completed = AtomicBoolean(false)
    private val eTags = ConcurrentHashSet<PartETag>()

    override suspend fun uploadPart(part: ByteArray, index: Int) {
        log.info { "Uploading part $index to ${response.key} (uploadId=${response.uploadId})" }
        val uploadPartRequest =
            UploadPartRequest()
                .withPartNumber(index)
                .withUploadId(response.uploadId)
                .withBucketName(bucket.s3BucketName)
                .withKey(response.key)
                .withInputStream(part.inputStream())
                .withPartSize(part.size.toLong())

        val response = amazonS3.uploadPart(uploadPartRequest)
        eTags.add(response.partETag)
    }

    override suspend fun complete(): S3Object {
        if (!completed.setOnce()) {
            log.warn {
                "Multipart upload already completed to ${response.key} (uploadId=${response.uploadId})"
            }
        } else if (eTags.isEmpty()) {
            log.warn { "Ignoring empty upload to ${response.key} (uploadId=${response.uploadId})" }
        } else {
            log.info {
                "Completing multipart upload to ${response.key} (uploadId=${response.uploadId})"
            }
            val completeMultipartUploadRequest =
                CompleteMultipartUploadRequest()
                    .withUploadId(response.uploadId)
                    .withPartETags(eTags.toList().sortedBy { it.partNumber })
                    .withBucketName(bucket.s3BucketName)
                    .withKey(response.key)
            amazonS3.completeMultipartUpload(completeMultipartUploadRequest)
        }

        return S3Object(response.key, bucket)
    }
}

class S3LegacyJavaClientFactory {
    private val clientBuilder = AmazonS3ClientBuilder.standard()

    fun createFromAssumeRole(
        role: AWSArnRoleConfiguration,
        creds: AwsAssumeRoleCredentials,
        bucket: S3BucketConfiguration
    ): S3LegacyJavaClient {
        val provider =
            STSAssumeRoleSessionCredentialsProvider.Builder(role.roleArn, AIRBYTE_STS_SESSION_NAME)
                .withExternalId(creds.externalId)
                .withStsClient(
                    AWSSecurityTokenServiceClient.builder()
                        .withRegion(Regions.DEFAULT_REGION)
                        .withCredentials(
                            AWSStaticCredentialsProvider(
                                BasicAWSCredentials(creds.accessKey, creds.secretKey)
                            )
                        )
                        .build()
                )
                .withAsyncRefreshExecutor(Executors.newSingleThreadExecutor(DaemonThreadFactory()))
                .build()
        val amazonS3 =
            clientBuilder
                .withCredentials(provider)
                .withRegion(bucket.s3BucketRegion.region)
                // the SDK defaults to RetryMode.LEGACY
                // (https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)
                // this _can_ be configured via environment variable, but it seems more reliable
                // to
                // configure it
                // programmatically
                .withClientConfiguration(ClientConfiguration().withRetryMode(RetryMode.STANDARD))
                .build()
        return S3LegacyJavaClient(amazonS3, bucket)
    }

    fun createFromAccessKey(
        keys: AWSAccessKeyConfiguration,
        bucket: S3BucketConfiguration
    ): S3Client {
        val awsCreds: AWSCredentials = BasicAWSCredentials(keys.accessKeyId, keys.secretAccessKey)
        val provider = AWSStaticCredentialsProvider(awsCreds)
        val builder = clientBuilder.withCredentials(provider)
        val amazonS3 =
            if (bucket.s3Endpoint.isNullOrEmpty()) {
                    builder.withRegion(bucket.s3BucketRegion.region)
                } else {
                    val clientConfiguration = ClientConfiguration().withProtocol(Protocol.HTTPS)
                    clientConfiguration.signerOverride = "AWSS3V4SignerType"

                    builder
                        .withEndpointConfiguration(
                            AwsClientBuilder.EndpointConfiguration(
                                bucket.s3Endpoint,
                                bucket.s3BucketRegion.region
                            )
                        )
                        .withPathStyleAccessEnabled(true)
                        .withClientConfiguration(clientConfiguration)
                }
                .build()
        return S3LegacyJavaClient(amazonS3, bucket)
    }
}
