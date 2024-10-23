/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CdcSourceConfiguration
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.time.Duration

private val log = KotlinLogging.logger {}

/** Mysql-specific implementation of [SourceConfiguration] */
data class MysqlSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    val incrementalConfiguration: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
    val debeziumKeepAliveInterval: Duration = Duration.ofMinutes(1),
    override val maxSnapshotReadDuration: Duration?
) : JdbcSourceConfiguration, CdcSourceConfiguration {
    override val global = incrementalConfiguration is CdcIncrementalConfiguration

    /** Required to inject [MysqlSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun mysqlSourceConfig(
            factory:
                SourceConfigurationFactory<
                    MysqlSourceConfigurationSpecification, MysqlSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<MysqlSourceConfigurationSpecification>,
        ): MysqlSourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialWaitDuration: Duration,
    val initialLoadTimeout: Duration,
    val serverTimezone: String?,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,
    RESET_SYNC,
}

@Singleton
class MysqlSourceConfigurationFactory @Inject constructor(val featureFlags: Set<FeatureFlag>) :
    SourceConfigurationFactory<MysqlSourceConfigurationSpecification, MysqlSourceConfiguration> {

    constructor() : this(emptySet())

    override fun makeWithoutExceptionHandling(
        pojo: MysqlSourceConfigurationSpecification,
    ): MysqlSourceConfiguration {
        val realHost: String = pojo.host
        val realPort: Int = pojo.port
        val sshTunnel: SshTunnelMethodConfiguration = pojo.getTunnelMethodValue()
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }

        // Parse URL parameters.
        val pattern = "^([^=]+)=(.*)$".toRegex()
        for (pair in (pojo.jdbcUrlParams ?: "").trim().split("&".toRegex())) {
            if (pair.isBlank()) {
                continue
            }
            val result: MatchResult? = pattern.matchEntire(pair)
            if (result == null) {
                log.warn { "ignoring invalid JDBC URL param '$pair'" }
            } else {
                val key: String = result.groupValues[1].trim()
                val urlEncodedValue: String = result.groupValues[2].trim()
                jdbcProperties[key] = URLDecoder.decode(urlEncodedValue, StandardCharsets.UTF_8)
            }
        }
        // Determine protocol and configure encryption.
        val encryption: Encryption = pojo.getEncryptionValue()
        val jdbcEncryption =
            when (encryption) {
                is EncryptionPreferred -> {
                    if (
                        featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT) &&
                            sshTunnel is SshNoTunnelMethod
                    ) {
                        throw ConfigErrorException(
                            "Connection from Airbyte Cloud requires " +
                                "SSL encryption or an SSH tunnel."
                        )
                    }
                    MysqlJdbcEncryption(sslMode = SSLMode.PREFERRED)
                }
                is EncryptionRequired -> MysqlJdbcEncryption(sslMode = SSLMode.REQUIRED)
                is SslVerifyCertificate ->
                    MysqlJdbcEncryption(
                        sslMode = SSLMode.VERIFY_CA,
                        caCertificate = encryption.sslCertificate,
                        clientCertificate = encryption.sslClientCertificate,
                        clientKey = encryption.sslClientKey,
                        clientKeyPassword = encryption.sslClientPassword
                    )
                is SslVerifyIdentity ->
                    MysqlJdbcEncryption(
                        sslMode = SSLMode.VERIFY_IDENTITY,
                        caCertificate = encryption.sslCertificate,
                        clientCertificate = encryption.sslClientCertificate,
                        clientKey = encryption.sslClientKey,
                        clientKeyPassword = encryption.sslClientPassword
                    )
            }
        val sslJdbcParameters = jdbcEncryption.parseSSLConfig()
        jdbcProperties.putAll(sslJdbcParameters)

        val cursorConfig = pojo.getCursorMethodConfigurationValue()
        val maxSnapshotReadTime: Duration? =
            when (cursorConfig is CdcCursor) {
                true -> cursorConfig.initialLoadTimeoutHours?.let { Duration.ofHours(it.toLong()) }
                else -> null
            }
        // Build JDBC URL
        val address = "%s:%d"
        val jdbcUrlFmt = "jdbc:mysql://${address}"
        jdbcProperties["useCursorFetch"] = "true"
        jdbcProperties["sessionVariables"] = "autocommit=0"
        val sshOpts = SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())
        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 0)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }
        val maxConcurrency: Int = pojo.concurrency ?: 0
        if ((pojo.concurrency ?: 0) <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }
        val incrementalConfiguration: IncrementalConfiguration =
            when (val incPojo = pojo.getCursorMethodConfigurationValue()) {
                UserDefinedCursor -> UserDefinedCursorIncrementalConfiguration
                is CdcCursor ->
                    CdcIncrementalConfiguration(
                        initialWaitDuration =
                            Duration.ofSeconds(incPojo.initialWaitTimeInSeconds!!.toLong()),
                        initialLoadTimeout =
                            Duration.ofHours(incPojo.initialLoadTimeoutHours!!.toLong()),
                        serverTimezone = incPojo.serverTimezone,
                        invalidCdcCursorPositionBehavior =
                            if (incPojo.invalidCdcCursorPositionBehavior == "Fail sync") {
                                InvalidCdcCursorPositionBehavior.FAIL_SYNC
                            } else {
                                InvalidCdcCursorPositionBehavior.RESET_SYNC
                            },
                    )
            }
        return MysqlSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            namespaces = setOf(pojo.database),
            incrementalConfiguration = incrementalConfiguration,
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
            maxSnapshotReadDuration = maxSnapshotReadTime
        )
    }
}
