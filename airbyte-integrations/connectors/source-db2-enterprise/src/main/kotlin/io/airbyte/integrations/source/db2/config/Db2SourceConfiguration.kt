/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2.config

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.jdbc.SSLCertificateUtils
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.File
import java.net.URI
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.time.Duration
import java.util.UUID
import kotlin.io.path.toPath

private val log = KotlinLogging.logger {}

/** DB2-specific implementation of [SourceConfiguration] */
data class Db2SourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    val incremental: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
) : JdbcSourceConfiguration {
    val cdc: CdcIncrementalConfiguration? = incremental as? CdcIncrementalConfiguration
    override val global: Boolean = false
    override val maxSnapshotReadDuration: Duration? = cdc?.initialLoadTimeout

    override fun isCdc(): Boolean {
        return cdc != null
    }

    // Required for Micronaut to inject a Db2SourceConfiguration bean directly
    @Factory
    private class MicronautFactory {
        @Singleton
        fun db2SourceConfig(
            factory:
                SourceConfigurationFactory<
                    Db2SourceConfigurationSpecification, Db2SourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<Db2SourceConfigurationSpecification>,
        ): Db2SourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialLoadTimeout: Duration,
) : IncrementalConfiguration

@Singleton
class Db2SourceConfigurationFactory :
    SourceConfigurationFactory<Db2SourceConfigurationSpecification, Db2SourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: Db2SourceConfigurationSpecification,
    ): Db2SourceConfiguration {
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
        jdbcProperties.putAll(encryptionJdbcProperties(encryption))
        // Build JDBC URL
        val address = "%s:%d"
        val jdbcUrlFmt = "jdbc:db2://${address}/${pojo.database}"
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
            when (val inc = pojo.getIncrementalConfigurationSpecificationValue()) {
                UserDefinedCursorConfigurationSpecification ->
                    UserDefinedCursorIncrementalConfiguration
                is CdcCursorConfigurationSpecification ->
                    CdcIncrementalConfiguration(
                        initialLoadTimeout =
                            Duration.ofHours(inc.initialLoadTimeoutHours!!.toLong()),
                    )
            }
        return Db2SourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            namespaces = pojo.schemas.toSet(),
            incremental = incrementalConfiguration,
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }

    private fun encryptionJdbcProperties(encryption: Encryption): Map<String, String> {
        val props = mutableMapOf<String, String>()
        when (encryption) {
            Unencrypted -> Unit
            is SslCertificate -> {
                val keyStorePass: String = UUID.randomUUID().toString()
                val keyStoreURI: URI =
                    SSLCertificateUtils.keyStoreFromCertificate(
                        certString = encryption.sslCertificate,
                        keyStorePassword = keyStorePass,
                    )
                val keyStoreFile: File = keyStoreURI.toPath().toFile()
                keyStoreFile.deleteOnExit()
                props["javax.net.ssl.trustStore"] = keyStoreFile.toString()
                props["javax.net.ssl.trustStoreType"] = "PKCS12"
                props["javax.net.ssl.trustStorePassword"] = keyStorePass
            }
        }
        return props
    }
}
