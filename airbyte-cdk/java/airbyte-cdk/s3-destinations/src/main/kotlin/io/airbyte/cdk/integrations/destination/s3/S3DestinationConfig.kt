/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.ClientConfiguration
import com.amazonaws.Protocol
import com.amazonaws.client.builder.AwsClientBuilder
import com.amazonaws.retry.RetryMode
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.constant.S3Constants
import io.airbyte.cdk.integrations.destination.s3.credential.S3AWSDefaultProfileCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3CredentialConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3CredentialType
import java.util.*
import javax.annotation.Nonnull
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * An S3 configuration. Typical usage sets at most one of `bucketPath` (necessary for more delicate
 * data syncing to S3)
 */
open class S3DestinationConfig {
    val endpoint: String?
    val bucketName: String?
    val bucketPath: String?
    val bucketRegion: String?
    val pathFormat: String?
    val s3CredentialConfig: S3CredentialConfig?
    val formatConfig: UploadFormatConfig?
    var fileNamePattern: String? = null
        private set

    private val lock = Any()
    private var s3Client: AmazonS3?
    fun getS3Client(): AmazonS3 {
        synchronized(lock) {
            s3Client?.let {
                return it
            }
            return resetS3Client()
        }
    }

    var isCheckIntegrity: Boolean = true
        private set

    var uploadThreadsCount: Int = S3StorageOperations.DEFAULT_UPLOAD_THREADS
        private set

    constructor(
        endpoint: String?,
        bucketName: String,
        bucketPath: String?,
        bucketRegion: String?,
        pathFormat: String?,
        credentialConfig: S3CredentialConfig?,
        formatConfig: UploadFormatConfig?,
        s3Client: AmazonS3
    ) {
        this.endpoint = endpoint
        this.bucketName = bucketName
        this.bucketPath = bucketPath
        this.bucketRegion = bucketRegion
        this.pathFormat = pathFormat
        this.s3CredentialConfig = credentialConfig
        this.formatConfig = formatConfig
        this.s3Client = s3Client
    }

    constructor(
        endpoint: String?,
        bucketName: String?,
        bucketPath: String?,
        bucketRegion: String?,
        pathFormat: String?,
        credentialConfig: S3CredentialConfig?,
        formatConfig: UploadFormatConfig?,
        s3Client: AmazonS3?,
        fileNamePattern: String?,
        checkIntegrity: Boolean,
        uploadThreadsCount: Int
    ) {
        this.endpoint = endpoint
        this.bucketName = bucketName
        this.bucketPath = bucketPath
        this.bucketRegion = bucketRegion
        this.pathFormat = pathFormat
        this.s3CredentialConfig = credentialConfig
        this.formatConfig = formatConfig
        this.s3Client = s3Client
        this.fileNamePattern = fileNamePattern
        this.isCheckIntegrity = checkIntegrity
        this.uploadThreadsCount = uploadThreadsCount
    }

    fun resetS3Client(): AmazonS3 {
        synchronized(lock) {
            s3Client?.shutdown()
            val s3Client = createS3Client()
            this.s3Client = s3Client
            return s3Client
        }
    }

    protected open fun createS3Client(): AmazonS3 {
        LOGGER.info("Creating S3 client...")

        val credentialsProvider = s3CredentialConfig!!.s3CredentialsProvider
        val credentialType = s3CredentialConfig.credentialType

        if (S3CredentialType.DEFAULT_PROFILE == credentialType) {
            return AmazonS3ClientBuilder.standard()
                .withRegion(bucketRegion)
                .withCredentials(credentialsProvider) // the SDK defaults to RetryMode.LEGACY
                // (https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)
                // this _can_ be configured via environment variable, but it seems more reliable to
                // configure it
                // programmatically
                .withClientConfiguration(ClientConfiguration().withRetryMode(RetryMode.STANDARD))
                .build()
        }

        if (null == endpoint || endpoint.isEmpty()) {
            return AmazonS3ClientBuilder.standard()
                .withCredentials(credentialsProvider)
                .withRegion(bucketRegion)
                .build()
        }

        val clientConfiguration = ClientConfiguration().withProtocol(Protocol.HTTPS)
        clientConfiguration.signerOverride = "AWSS3V4SignerType"

        return AmazonS3ClientBuilder.standard()
            .withEndpointConfiguration(
                AwsClientBuilder.EndpointConfiguration(endpoint, bucketRegion)
            )
            .withPathStyleAccessEnabled(true)
            .withClientConfiguration(clientConfiguration)
            .withCredentials(credentialsProvider)
            .build()
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as S3DestinationConfig
        return endpoint == that.endpoint &&
            bucketName == that.bucketName &&
            bucketPath == that.bucketPath &&
            bucketRegion == that.bucketRegion &&
            s3CredentialConfig == that.s3CredentialConfig &&
            formatConfig == that.formatConfig
    }

    override fun hashCode(): Int {
        return Objects.hash(
            endpoint,
            bucketName,
            bucketPath,
            bucketRegion,
            s3CredentialConfig,
            formatConfig
        )
    }

    class Builder(
        private var bucketName: String?,
        private var bucketPath: String,
        private var bucketRegion: String?
    ) {
        private var endpoint: String? = ""
        private var pathFormat = S3DestinationConstants.DEFAULT_PATH_FORMAT

        private lateinit var credentialConfig: S3CredentialConfig
        private var formatConfig: UploadFormatConfig? = null
        private var s3Client: AmazonS3? = null
        private var fileNamePattern: String? = null

        private var checkIntegrity = true

        private var uploadThreadsCount = S3StorageOperations.DEFAULT_UPLOAD_THREADS

        fun withBucketName(bucketName: String): Builder {
            this.bucketName = bucketName
            return this
        }

        fun withFileNamePattern(fileNamePattern: String?): Builder {
            this.fileNamePattern = fileNamePattern
            return this
        }

        fun withBucketPath(bucketPath: String): Builder {
            this.bucketPath = bucketPath
            return this
        }

        fun withBucketRegion(bucketRegion: String?): Builder {
            this.bucketRegion = bucketRegion
            return this
        }

        fun withPathFormat(pathFormat: String): Builder {
            this.pathFormat = pathFormat
            return this
        }

        fun withEndpoint(endpoint: String?): Builder {
            this.endpoint = endpoint
            return this
        }

        fun withFormatConfig(formatConfig: UploadFormatConfig?): Builder {
            this.formatConfig = formatConfig
            return this
        }

        fun withAccessKeyCredential(accessKeyId: String?, secretAccessKey: String?): Builder {
            this.credentialConfig = S3AccessKeyCredentialConfig(accessKeyId, secretAccessKey)
            return this
        }

        fun withCredentialConfig(credentialConfig: S3CredentialConfig): Builder {
            this.credentialConfig = credentialConfig
            return this
        }

        fun withS3Client(s3Client: AmazonS3): Builder {
            this.s3Client = s3Client
            return this
        }

        fun withCheckIntegrity(checkIntegrity: Boolean): Builder {
            this.checkIntegrity = checkIntegrity
            return this
        }

        fun withUploadThreadsCount(uploadThreadsCount: Int): Builder {
            this.uploadThreadsCount = uploadThreadsCount
            return this
        }

        fun get(): S3DestinationConfig {
            return S3DestinationConfig(
                endpoint,
                bucketName,
                bucketPath,
                bucketRegion,
                pathFormat,
                credentialConfig,
                formatConfig,
                s3Client,
                fileNamePattern,
                checkIntegrity,
                uploadThreadsCount
            )
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(S3DestinationConfig::class.java)
        private const val R2_INSTANCE_URL = "https://%s.r2.cloudflarestorage.com"

        @JvmStatic
        fun create(bucketName: String?, bucketPath: String, bucketRegion: String?): Builder {
            return Builder(bucketName, bucketPath, bucketRegion)
        }

        @JvmStatic
        fun create(config: S3DestinationConfig): Builder {
            return Builder(config.bucketName, config.bucketPath!!, config.bucketRegion)
                .withEndpoint(config.endpoint)
                .withCredentialConfig(config.s3CredentialConfig!!)
                .withFormatConfig(config.formatConfig)
        }

        @JvmStatic
        fun getS3DestinationConfig(@Nonnull config: JsonNode): S3DestinationConfig {
            return getS3DestinationConfig(config, StorageProvider.AWS_S3)
        }

        @JvmStatic
        fun getS3DestinationConfig(
            @Nonnull config: JsonNode,
            @Nonnull storageProvider: StorageProvider
        ): S3DestinationConfig {
            var builder =
                create(
                    getProperty(config, S3Constants.S_3_BUCKET_NAME),
                    "",
                    getProperty(config, S3Constants.S_3_BUCKET_REGION)
                )

            if (config.has(S3Constants.S_3_BUCKET_PATH)) {
                builder = builder.withBucketPath(config[S3Constants.S_3_BUCKET_PATH].asText())
            }

            if (config.has(S3Constants.FILE_NAME_PATTERN)) {
                builder =
                    builder.withFileNamePattern(config[S3Constants.FILE_NAME_PATTERN].asText())
            }

            if (config.has(S3Constants.S_3_PATH_FORMAT)) {
                builder = builder.withPathFormat(config[S3Constants.S_3_PATH_FORMAT].asText())
            }

            when (storageProvider) {
                StorageProvider.CF_R2 -> {
                    if (config.has(S3Constants.ACCOUNT_ID)) {
                        val endpoint =
                            String.format(
                                R2_INSTANCE_URL,
                                getProperty(config, S3Constants.ACCOUNT_ID)
                            )
                        builder = builder.withEndpoint(endpoint)
                    }
                    builder =
                        builder
                            .withCheckIntegrity(
                                false
                            ) // https://developers.cloudflare.com/r2/platform/s3-compatibility/api/#implemented-object-level-operations
                            // 3 or less
                            .withUploadThreadsCount(S3StorageOperations.R2_UPLOAD_THREADS)
                }
                else -> {
                    if (config.has(S3Constants.S_3_ENDPOINT)) {
                        builder = builder.withEndpoint(config[S3Constants.S_3_ENDPOINT].asText())
                    }
                }
            }
            val credentialConfig =
                if (config.has(S3Constants.ACCESS_KEY_ID)) {
                    S3AccessKeyCredentialConfig(
                        getProperty(config, S3Constants.ACCESS_KEY_ID),
                        getProperty(config, S3Constants.SECRET_ACCESS_KEY)
                    )
                } else {
                    S3AWSDefaultProfileCredentialConfig()
                }
            builder = builder.withCredentialConfig(credentialConfig)

            // In the "normal" S3 destination, this is never null. However, the Redshift and
            // Snowflake copy
            // destinations don't set a Format config.
            if (config.has("format")) {
                builder =
                    builder.withFormatConfig(
                        UploadFormatConfigFactory.getUploadFormatConfig(config)
                    )
            }

            return builder.get()
        }

        private fun getProperty(config: JsonNode, @Nonnull key: String): String? {
            val node: JsonNode? = config.get(key)
            return node?.asText()
        }
    }
}
