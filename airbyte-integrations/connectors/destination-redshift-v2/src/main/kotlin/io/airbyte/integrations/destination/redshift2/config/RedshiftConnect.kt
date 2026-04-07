/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.config

import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.createTunnelSession
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.time.Duration.Companion.minutes
import kotlin.time.Duration.Companion.seconds
import org.apache.sshd.common.util.net.SshdSocketAddress

private val log = KotlinLogging.logger {}

/**
 * Manages Redshift JDBC and S3 connections with support for:
 * - HikariCP connection pooling
 * - SSL encryption (always enabled)
 * - SSH tunnel resolution (key-auth and password-auth)
 * - Configurable JDBC URL parameters
 * - S3 client creation for staging operations
 */
@Singleton
class RedshiftConnect(
    private val configuration: RedshiftConfiguration,
) {

    /**
     * Resolves the database endpoint, tunneling through SSH if configured.
     *
     * When an SSH tunnel is configured, this opens a local port-forward to the remote
     * Redshift host and returns the tunnel's local address. When no tunnel is configured,
     * the direct host/port from the configuration is returned.
     */
    fun resolveEndpoint(): Pair<String, Int> {
        return when (val ssh = configuration.tunnelMethod) {
            is SshKeyAuthTunnelMethod,
            is SshPasswordAuthTunnelMethod -> {
                val remote = SshdSocketAddress(configuration.host, configuration.port)
                val sshConnectionOptions =
                    SshConnectionOptions.fromAdditionalProperties(emptyMap())
                val tunnel = createTunnelSession(remote, ssh, sshConnectionOptions)
                log.info {
                    "SSH tunnel established: ${configuration.host}:${configuration.port} " +
                        "-> ${tunnel.address.hostName}:${tunnel.address.port}"
                }
                tunnel.address.hostName to tunnel.address.port
            }
            is SshNoTunnelMethod,
            null -> configuration.host to configuration.port
        }
    }

    /**
     * Creates a fully configured [HikariDataSource] for Redshift.
     *
     * The DataSource is configured with:
     * - SSL enabled with non-validating factory (standard for Redshift)
     * - Redshift driver-level connect timeout of 120 seconds
     * - Connection keepalive at 30-second intervals
     * - Pool sizing: max 10, min idle 0 (connections created on demand)
     */
    fun createDataSource(): HikariDataSource {
        val (resolvedHost, resolvedPort) = resolveEndpoint()
        val jdbcUrl = buildJdbcUrl(resolvedHost, resolvedPort)

        log.info { "Creating Redshift DataSource for $resolvedHost:$resolvedPort/${configuration.database}" }

        val hikariConfig =
            HikariConfig().apply {
                connectionTimeout = 1.minutes.inWholeMilliseconds
                maximumPoolSize = 10
                minimumIdle = 0
                initializationFailTimeout = -1
                leakDetectionThreshold = 5.minutes.inWholeMilliseconds
                keepaliveTime = 30.seconds.inWholeMilliseconds
                driverClassName = DRIVER_CLASS
                this.jdbcUrl = jdbcUrl
                username = configuration.username
                password = configuration.password
                schema = configuration.schema

                // SSL: always enabled for Redshift connections
                addDataSourceProperty("ssl", "true")
                addDataSourceProperty("sslfactory", SSL_FACTORY)

                // Redshift driver-level connect timeout (seconds).
                // This is distinct from HikariCP's connectionTimeout which governs
                // how long to wait for a connection from the pool.
                addDataSourceProperty("connectTimeout", DRIVER_CONNECT_TIMEOUT_SECONDS)

                // Connection validation
                connectionTestQuery = "SELECT 1"
            }

        return HikariDataSource(hikariConfig)
    }

    /**
     * Creates an [AmazonS3] client from the S3 staging configuration.
     *
     * Uses static credentials (access key + secret key) and the configured region.
     * Requires [RedshiftConfiguration.uploadingMethod] to be non-null.
     *
     * @throws IllegalStateException if S3 staging configuration is not provided.
     */
    fun createS3Client(): AmazonS3 {
        val s3Config =
            configuration.uploadingMethod
                ?: throw IllegalStateException(
                    "S3 staging configuration is required but not provided"
                )

        log.info {
            "Creating S3 client for bucket '${s3Config.s3BucketName}' " +
                "in region '${s3Config.s3BucketRegion ?: DEFAULT_S3_REGION}'"
        }

        return AmazonS3ClientBuilder.standard()
            .withCredentials(
                AWSStaticCredentialsProvider(
                    BasicAWSCredentials(s3Config.accessKeyId, s3Config.secretAccessKey)
                )
            )
            .withRegion(s3Config.s3BucketRegion?.ifBlank { DEFAULT_S3_REGION } ?: DEFAULT_S3_REGION)
            .build()
    }

    private fun buildJdbcUrl(resolvedHost: String, resolvedPort: Int): String {
        val baseUrl = "jdbc:redshift://$resolvedHost:$resolvedPort/${configuration.database}"
        return if (configuration.jdbcUrlParams.isNullOrBlank()) {
            baseUrl
        } else {
            "$baseUrl?${configuration.jdbcUrlParams}"
        }
    }

    companion object {
        const val DRIVER_CLASS = "com.amazon.redshift.jdbc42.Driver"
        const val SSL_FACTORY = "com.amazon.redshift.ssl.NonValidatingFactory"
        const val DEFAULT_S3_REGION = "us-east-1"

        /** Redshift JDBC driver-level connect timeout in seconds. */
        const val DRIVER_CONNECT_TIMEOUT_SECONDS = "120"
    }
}
