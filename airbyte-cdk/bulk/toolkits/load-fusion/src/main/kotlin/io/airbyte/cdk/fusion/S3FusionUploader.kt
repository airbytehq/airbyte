/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.fusion

import java.nio.file.Path
import java.time.Duration
import java.util.concurrent.CompletableFuture
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.core.async.AsyncRequestBody
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration
import software.amazon.awssdk.http.nio.netty.NettyNioAsyncHttpClient
import software.amazon.awssdk.http.urlconnection.UrlConnectionHttpClient
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.retries.StandardRetryStrategy
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import software.amazon.awssdk.services.sts.StsClient
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest

interface FusionUploader : AutoCloseable {
    fun upload(path: Path, key: String, metadata: Map<String, String>): CompletableFuture<*>
    fun uploadJson(bytes: ByteArray, key: String): CompletableFuture<*>
}

class S3FusionUploader
@JvmOverloads
constructor(
    private val config: FusionConfiguration,
    private val contentType: String = "application/gzip",
) : FusionUploader {
    private val bootstrap: AwsCredentialsProvider =
        if (config.accessKeyId != null && config.secretAccessKey != null) {
            StaticCredentialsProvider.create(
                AwsBasicCredentials.create(config.accessKeyId, config.secretAccessKey)
            )
        } else {
            DefaultCredentialsProvider.builder().build()
        }
    private val sts =
        StsClient.builder()
            .region(Region.of(config.region))
            .credentialsProvider(bootstrap)
            .httpClientBuilder(UrlConnectionHttpClient.builder())
            .build()
    private val credentials =
        StsAssumeRoleCredentialsProvider.builder()
            .stsClient(sts)
            .refreshRequest(
                AssumeRoleRequest.builder()
                    .roleArn(config.roleArn)
                    .roleSessionName("airbyte-fusion-${java.util.UUID.randomUUID()}")
                    .apply { config.externalId?.let { externalId(it) } }
                    .build()
            )
            .build()
    private val s3 =
        S3AsyncClient.builder()
            .region(Region.of(config.region))
            .credentialsProvider(credentials)
            .httpClientBuilder(
                NettyNioAsyncHttpClient.builder()
                    .maxConcurrency(16)
                    .connectionTimeout(Duration.ofSeconds(10))
            )
            .overrideConfiguration(
                ClientOverrideConfiguration.builder()
                    .retryStrategy(StandardRetryStrategy.builder().maxAttempts(3).build())
                    .apiCallAttemptTimeout(Duration.ofMinutes(2))
                    .apiCallTimeout(Duration.ofMinutes(30))
                    .build()
            )
            .build()

    override fun upload(
        path: Path,
        key: String,
        metadata: Map<String, String>
    ): CompletableFuture<*> {
        val request =
            PutObjectRequest.builder()
                .bucket(config.bucket)
                .key(key)
                .contentType(contentType)
                .metadata(metadata)
                .build()
        return s3.putObject(request, AsyncRequestBody.fromFile(path))
    }

    override fun uploadJson(bytes: ByteArray, key: String): CompletableFuture<*> =
        s3.putObject(
            PutObjectRequest.builder()
                .bucket(config.bucket)
                .key(key)
                .contentType("application/json")
                .build(),
            AsyncRequestBody.fromBytes(bytes)
        )

    override fun close() {
        s3.close()
        credentials.close()
        sts.close()
        (bootstrap as? AutoCloseable)?.close()
    }
}
