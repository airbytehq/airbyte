package io.airbyte.integrations.destination.snowflake.copy

import java.nio.file.Path
import java.time.Duration
import java.util.concurrent.CompletableFuture
import software.amazon.awssdk.core.async.AsyncRequestBody
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration
import software.amazon.awssdk.core.retry.RetryPolicy
import software.amazon.awssdk.http.nio.netty.NettyNioAsyncHttpClient
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import software.amazon.awssdk.services.sts.StsClient
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider

internal class S3CsvUploader(private val config: S3CopyConfiguration) : AutoCloseable {
    private val bootstrap = DefaultCredentialsProvider.create()
    private val sts = StsClient.builder()
        .region(Region.of(config.region))
        .credentialsProvider(bootstrap)
        .build()
    private val credentials = StsAssumeRoleCredentialsProvider.builder()
        .stsClient(sts)
        .refreshRequest(
            AssumeRoleRequest.builder().roleArn(config.roleArn)
                .roleSessionName("airbyte-snowflake-${java.util.UUID.randomUUID()}")
                .apply { config.externalId?.let { externalId(it) } }
                .build()
        )
        .build()
    private val s3 = S3AsyncClient.builder()
        .region(Region.of(config.region))
        .credentialsProvider(credentials)
        .httpClient(
            NettyNioAsyncHttpClient.builder().maxConcurrency(16)
                .connectionTimeout(Duration.ofSeconds(10)).build()
        )
        .overrideConfiguration(
            ClientOverrideConfiguration.builder().retryPolicy(RetryPolicy.builder().numRetries(2).build())
                .apiCallAttemptTimeout(Duration.ofMinutes(2))
                .apiCallTimeout(Duration.ofMinutes(30)).build()
        ).build()

    fun upload(path: Path, key: String, metadata: Map<String, String>): CompletableFuture<*> {
        val request = PutObjectRequest.builder().bucket(config.bucket).key(key)
            .contentType("application/gzip").metadata(metadata).build()
        return s3.putObject(request, AsyncRequestBody.fromFile(path))
    }

    fun uploadJson(bytes: ByteArray, key: String): CompletableFuture<*> =
        s3.putObject(
            PutObjectRequest.builder().bucket(config.bucket).key(key).contentType("application/json").build(),
            AsyncRequestBody.fromBytes(bytes)
        )

    override fun close() {
        s3.close(); credentials.close(); sts.close(); bootstrap.close()
    }
}
