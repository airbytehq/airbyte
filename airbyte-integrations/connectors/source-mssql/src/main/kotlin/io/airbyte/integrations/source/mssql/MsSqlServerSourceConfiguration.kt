/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.*
import io.airbyte.cdk.jdbc.SSLCertificateUtils
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.time.Duration
import org.apache.commons.lang3.RandomStringUtils

private val log = KotlinLogging.logger {}

class MsSqlServerSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
    val incrementalReplicationConfiguration: IncrementalConfiguration,
    val databaseName: String,
) : JdbcSourceConfiguration, CdcSourceConfiguration {
    override val global = incrementalReplicationConfiguration is CdcIncrementalConfiguration
    override val maxSnapshotReadDuration: Duration? =
        (incrementalReplicationConfiguration as? CdcIncrementalConfiguration)?.initialLoadTimeout

    /** Required to inject [MsSqlServerSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun mssqlServerSourceConfig(
            factory:
                SourceConfigurationFactory<
                    MsSqlServerSourceConfigurationSpecification, MsSqlServerSourceConfiguration>,
            supplier:
                ConfigurationSpecificationSupplier<MsSqlServerSourceConfigurationSpecification>,
        ): MsSqlServerSourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data class UserDefinedCursorIncrementalConfiguration(val excludeTodaysData: Boolean = false) :
    IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialWaitingSeconds: Duration,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
    val initialLoadTimeout: Duration,
    val pollIntervalMs: Int
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,
    RESET_SYNC,
}

@Singleton
class MsSqlServerSourceConfigurationFactory
@Inject
constructor(
    val featureFlags: Set<FeatureFlag>,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}")
    val dataChannelMedium: String = DataChannelMedium.STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
) :
    SourceConfigurationFactory<
        MsSqlServerSourceConfigurationSpecification, MsSqlServerSourceConfiguration> {

    constructor() : this(emptySet(), DataChannelMedium.STDIO.name, emptyList())

    override fun makeWithoutExceptionHandling(
        pojo: MsSqlServerSourceConfigurationSpecification,
    ): MsSqlServerSourceConfiguration {
        val incrementalSpec = pojo.getIncrementalValue()
        val incrementalReplicationConfiguration =
            when (incrementalSpec) {
                is UserDefinedCursor -> {
                    UserDefinedCursorIncrementalConfiguration(
                        excludeTodaysData = incrementalSpec.excludeTodaysData ?: false
                    )
                }
                is Cdc -> {
                    val initialWaitingSeconds: Duration =
                        Duration.ofSeconds(incrementalSpec.initialWaitingSeconds?.toLong() ?: 300L)
                    val initialLoadTimeout: Duration =
                        Duration.ofHours(incrementalSpec.initialLoadTimeoutHours?.toLong() ?: 8L)
                    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior =
                        if (incrementalSpec.invalidCdcCursorPositionBehavior == "Fail sync") {
                            InvalidCdcCursorPositionBehavior.FAIL_SYNC
                        } else {
                            InvalidCdcCursorPositionBehavior.RESET_SYNC
                        }

                    // Validate poll interval vs heartbeat interval
                    val pollIntervalMs = incrementalSpec.pollIntervalMs ?: 500
                    val heartbeatIntervalMs =
                        MsSqlServerSourceConfigurationSpecification.DEFAULT_HEARTBEAT_INTERVAL_MS
                    if (pollIntervalMs >= heartbeatIntervalMs) {
                        throw ConfigErrorException(
                            "Poll interval ($pollIntervalMs ms) must be smaller than heartbeat interval ($heartbeatIntervalMs ms). " +
                                "Please reduce the poll interval to a value less than $heartbeatIntervalMs ms."
                        )
                    }

                    CdcIncrementalConfiguration(
                        initialWaitingSeconds,
                        invalidCdcCursorPositionBehavior,
                        initialLoadTimeout,
                        pollIntervalMs,
                    )
                }
            }

        val sshTunnel: SshTunnelMethodConfiguration? = pojo.getTunnelMethodValue()

        // Check if encryption was explicitly set in JSON (encryptionJson != null)
        // vs using the default value (encryptionJson == null).
        // Old connector used "ssl_method" field which was optional, so legacy configs
        // won't have ssl_mode at all, resulting in encryptionJson being null.
        val isLegacyConfig = pojo.encryptionJson == null
        val jdbcEncryption =
            when (val encryptionSpec: EncryptionSpecification? = pojo.getEncryptionValue()) {
                is MsSqlServerEncryptionDisabledConfigurationSpecification -> {
                    // For legacy configs without ssl_mode field, allow unencrypted for backward
                    // compatibility
                    // even in cloud deployments. This handles migration from old connector
                    // versions.
                    if (isLegacyConfig) {
                        log.warn {
                            "No encryption configuration found in JSON. " +
                                "This appears to be a legacy configuration migrated from an older connector version. " +
                                "Consider adding SSL encryption for better security."
                        }
                        mapOf("encrypt" to "false", "trustServerCertificate" to "true")
                    } else {
                        // Explicitly disabled encryption (user set ssl_mode.mode = "unencrypted")
                        // should fail in cloud without SSH tunnel
                        if (
                            featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT) &&
                                sshTunnel is SshNoTunnelMethod
                        ) {
                            throw ConfigErrorException(
                                "Connection from Airbyte Cloud requires " +
                                    "SSL encryption or an SSH tunnel."
                            )
                        } else {
                            mapOf("encrypt" to "false", "trustServerCertificate" to "true")
                        }
                    }
                }
                null -> {
                    // This should never happen since getEncryptionValue() has a default
                    mapOf("encrypt" to "false", "trustServerCertificate" to "true")
                }
                is MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification ->
                    mapOf("encrypt" to "true", "trustServerCertificate" to "true")
                is SslVerifyCertificate -> {
                    val certificate = encryptionSpec.certificate
                    val trustStoreProperties =
                        if (certificate == null) {
                            emptyMap()
                        } else {
                            val password = RandomStringUtils.secure().next(100)
                            val keyStoreUri =
                                SSLCertificateUtils.keyStoreFromCertificate(certificate, password)
                            mapOf(
                                "trustStore" to keyStoreUri.path,
                                "trustStorePassword" to password
                            )
                        }
                    val hostNameInCertificate = encryptionSpec.hostNameInCertificate
                    val hostNameProperties =
                        if (hostNameInCertificate == null) {
                            emptyMap()
                        } else {
                            mapOf("hostNameInCertificate" to hostNameInCertificate)
                        }
                    trustStoreProperties +
                        hostNameProperties +
                        mapOf("encrypt" to "true", "trustServerCertificate" to "false")
                }
            }

        // Parse JDBC URL parameters
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        jdbcProperties["password"] = pojo.password

        // Parse URL parameters from jdbcUrlParams
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
        jdbcProperties.putAll(jdbcEncryption)

        // Validate and process configuration values
        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 300L)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }

        var maxConcurrency: Int? = pojo.concurrency

        log.info { "maxConcurrency: $maxConcurrency. socket paths: ${socketPaths.size}" }

        // If maxConcurrency is set, we use it.
        // Otherwise, we use the number of socket paths provided for speed mode
        // Or 1 for legacy mode
        maxConcurrency =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                DataChannelMedium.STDIO -> maxConcurrency ?: 1
                DataChannelMedium.SOCKET -> maxConcurrency ?: socketPaths.size
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        if (maxConcurrency <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }

        return MsSqlServerSourceConfiguration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = sshTunnel,
            sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
            checkpointTargetInterval = checkpointTargetInterval,
            jdbcUrlFmt = "jdbc:sqlserver://%s:%d;databaseName=${pojo.database}",
            namespaces = pojo.schemas?.takeIf { it.isNotEmpty() }?.toSet() ?: emptySet(),
            jdbcProperties = jdbcProperties,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
            debeziumHeartbeatInterval =
                Duration.ofMillis(
                    MsSqlServerSourceConfigurationSpecification.DEFAULT_HEARTBEAT_INTERVAL_MS
                ),
            incrementalReplicationConfiguration = incrementalReplicationConfiguration,
            databaseName = pojo.database
        )
    }
}
