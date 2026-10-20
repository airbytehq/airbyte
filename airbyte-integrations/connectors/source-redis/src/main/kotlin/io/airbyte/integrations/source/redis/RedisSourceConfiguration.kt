/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.Duration

private val log = KotlinLogging.logger {}

data class RedisSourceConfiguration(
    val host: String,
    val port: Int,
    val username: String?,
    val password: String?,
    val database: Int,
    val sslMode: RedisSslModeConfiguration,
    val keyPattern: String,
    val scanBatchSize: Int,
    val maxDbConnections: Int?,
    override val maxConcurrency: Int,
    override val realHost: String,
    override val realPort: Int,
    override val checkpointTargetInterval: Duration,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100),
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(emptyMap()),
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
) : SourceConfiguration {
    override fun toString(): String =
        "RedisSourceConfiguration(host=$host, port=$port, username=$username, password=*****, " +
            "database=$database, sslMode=$sslMode, keyPattern=$keyPattern, " +
            "scanBatchSize=$scanBatchSize, maxDbConnections=$maxDbConnections, " +
            "maxConcurrency=$maxConcurrency)"

    @Factory
    private class MicronautFactory {
        @Singleton
        fun redisSourceConfiguration(
            factory:
                SourceConfigurationFactory<
                    RedisSourceConfigurationSpecification,
                    RedisSourceConfiguration,
                >,
            supplier: ConfigurationSpecificationSupplier<RedisSourceConfigurationSpecification>,
        ): RedisSourceConfiguration = factory.make(supplier.get())
    }
}

@Singleton
class RedisSourceConfigurationFactory
@Inject
constructor(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}")
    private val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    private val socketPaths: List<String> = emptyList(),
) : SourceConfigurationFactory<RedisSourceConfigurationSpecification, RedisSourceConfiguration> {
    override fun make(spec: RedisSourceConfigurationSpecification): RedisSourceConfiguration =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: ConfigErrorException) {
            throw e
        } catch (e: Exception) {
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }

    override fun makeWithoutExceptionHandling(
        pojo: RedisSourceConfigurationSpecification,
    ): RedisSourceConfiguration {
        val host =
            try {
                pojo.host.trim().ifBlank { throw ConfigErrorException("'host' must not be blank.") }
            } catch (_: UninitializedPropertyAccessException) {
                throw ConfigErrorException("The 'host' property is required.")
            }
        val port = pojo.port
        if (port !in 1..65535) {
            throw ConfigErrorException("'port' must be between 1 and 65535, got $port.")
        }
        val database = pojo.database ?: RedisSourceConfigurationSpecification.DEFAULT_DATABASE
        if (database < 0) {
            throw ConfigErrorException("'database' must be at least 0, got $database.")
        }
        val scanBatchSize =
            pojo.scanBatchSize ?: RedisSourceConfigurationSpecification.DEFAULT_SCAN_BATCH_SIZE
        if (scanBatchSize < 1) {
            throw ConfigErrorException("'scan_batch_size' must be at least 1, got $scanBatchSize.")
        }
        val checkpointTargetIntervalSeconds =
            pojo.checkpointTargetIntervalSeconds
                ?: RedisSourceConfigurationSpecification.DEFAULT_CHECKPOINT_TARGET_INTERVAL_SECONDS
        if (checkpointTargetIntervalSeconds < 1) {
            throw ConfigErrorException(
                "'checkpoint_target_interval_seconds' must be at least 1, got $checkpointTargetIntervalSeconds.",
            )
        }
        val maxDbConnections = pojo.maxDbConnections
        if (maxDbConnections != null && maxDbConnections < 1) {
            throw ConfigErrorException(
                "'max_db_connections' must be at least 1, got $maxDbConnections.",
            )
        }
        val tunnelMethod = pojo.getTunnelMethodValue() ?: pojo.tunnelMethod.asSshTunnelMethod()
        val sslMode = pojo.getSslModeValue() ?: pojo.sslMode.asSslMode()
        val clientCertificate: String?
        val clientKey: String?
        val clientKeyPassword: String?
        when (sslMode) {
            RedisSslDisabled,
            RedisSslRequired -> {
                clientCertificate = null
                clientKey = null
                clientKeyPassword = null
            }
            is RedisSslVerifyCa -> {
                clientCertificate = sslMode.clientCertificate
                clientKey = sslMode.clientKey
                clientKeyPassword = sslMode.clientKeyPassword
            }
            is RedisSslVerifyFull -> {
                clientCertificate = sslMode.clientCertificate
                clientKey = sslMode.clientKey
                clientKeyPassword = sslMode.clientKeyPassword
            }
        }
        if ((clientCertificate == null) != (clientKey == null)) {
            throw ConfigErrorException(
                "Both 'client_certificate' and 'client_key' are required for mutual TLS.",
            )
        }
        if (clientKeyPassword != null && clientKey == null) {
            throw ConfigErrorException("'client_key_password' requires a 'client_key'.")
        }
        if (sslMode is RedisSslVerifyFull && tunnelMethod !is SshNoTunnelMethod) {
            throw ConfigErrorException(
                "'verify-full' cannot be used with an SSH tunnel because the tunnel endpoint does not match the Redis server hostname. Use 'verify-ca' instead.",
            )
        }
        val maxConcurrency =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> maxDbConnections ?: 1
                SOCKET -> maxDbConnections ?: socketPaths.size
            }
        if (maxConcurrency < 1) {
            throw ConfigErrorException(
                "Effective max_db_connections must be positive; got $maxConcurrency.",
            )
        }
        log.info { "Effective Redis connection concurrency: $maxConcurrency." }
        return RedisSourceConfiguration(
            host = host,
            port = port,
            username = pojo.username?.trim()?.ifBlank { null },
            password = pojo.password?.takeIf(String::isNotBlank),
            database = database,
            sslMode = sslMode,
            keyPattern =
                pojo.keyPattern ?: RedisSourceConfigurationSpecification.DEFAULT_KEY_PATTERN,
            scanBatchSize = scanBatchSize,
            maxDbConnections = maxDbConnections,
            maxConcurrency = maxConcurrency,
            realHost = host,
            realPort = port,
            checkpointTargetInterval = Duration.ofSeconds(checkpointTargetIntervalSeconds.toLong()),
            sshTunnel = tunnelMethod,
        )
    }
}
