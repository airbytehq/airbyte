/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CdcSourceConfiguration
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

/** Oracle-specific implementation of [SourceConfiguration] */
data class OracleSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    val defaultSchema: String,
    override val namespaces: Set<String>,
    val incremental: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
) : JdbcSourceConfiguration, CdcSourceConfiguration {
    val cdc: CdcIncrementalConfiguration? = incremental as? CdcIncrementalConfiguration

    override val global: Boolean = cdc != null
    override val maxSnapshotReadDuration: Duration? = cdc?.initialLoadTimeout

    /** Required to inject [OracleSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun oracleSourceConfig(
            factory:
                SourceConfigurationFactory<
                    OracleSourceConfigurationSpecification, OracleSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<OracleSourceConfigurationSpecification>,
        ): OracleSourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialLoadTimeout: Duration,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
    val shutdownTimeout: Duration,
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,
    RESET_SYNC,
}

@Singleton
class OracleSourceConfigurationFactory :
    SourceConfigurationFactory<OracleSourceConfigurationSpecification, OracleSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: OracleSourceConfigurationSpecification,
    ): OracleSourceConfiguration {
        val realHost: String = pojo.host
        val realPort: Int = pojo.port
        val sshTunnel: SshTunnelMethodConfiguration = pojo.getTunnelMethodValue()
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }
        /*
         * The property useFetchSizeWithLongColumn required to select LONG or LONG RAW columns.
         * Oracle recommends avoiding LONG and LONG RAW columns. Use LOB instead.
         * They are included in Oracle only for legacy reasons.
         *
         * THIS IS A THIN ONLY PROPERTY. IT SHOULD NOT BE USED WITH ANY OTHER DRIVERS.
         *
         * See
         * https://docs.oracle.com/cd/E11882_01/appdev.112/e13995/oracle/jdbc/OracleDriver.html
         * https://docs.oracle.com/cd/B19306_01/java.102/b14355/jstreams.htm#i1014085
         */
        jdbcProperties["oracle.jdbc.useFetchSizeWithLongColumn"] = "true"
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
        val protocol: String = if (encryption is SslCertificate) "TCPS" else "TCP"
        jdbcProperties.putAll(encryptionJdbcProperties(encryption))
        // Build JDBC URL
        val address = "(ADDRESS=(PROTOCOL=$protocol)(HOST=%s)(PORT=%d))"
        val connectionData: ConnectionData = pojo.getConnectionDataValue()
        val (connectDataType: String, connectDataValue: String) =
            when (connectionData) {
                is ServiceName -> "SERVICE_NAME" to connectionData.serviceName
                is Sid -> "SID" to connectionData.sid
            }
        val connectData = "(CONNECT_DATA=($connectDataType=$connectDataValue))"
        val jdbcUrlFmt = "jdbc:oracle:thin:@(DESCRIPTION=${address}$connectData)"
        val defaultSchema: String = pojo.username.uppercase()
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
                        invalidCdcCursorPositionBehavior =
                            when (inc.invalidCdcCursorPositionBehavior) {
                                "Fail sync" -> InvalidCdcCursorPositionBehavior.FAIL_SYNC
                                "Re-sync data" -> InvalidCdcCursorPositionBehavior.RESET_SYNC
                                else ->
                                    throw ConfigErrorException(
                                        "Unknown value ${inc.invalidCdcCursorPositionBehavior}"
                                    )
                            },
                        shutdownTimeout =
                            Duration.ofSeconds(inc.debeziumShutdownTimeoutSeconds!!.toLong()),
                    )
            }
        return OracleSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            defaultSchema = defaultSchema,
            namespaces = pojo.schemas?.toSet() ?: setOf(defaultSchema),
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
            is EncryptionAlgorithm -> {
                val algorithm: String = encryption.encryptionAlgorithm
                props["oracle.net.encryption_client"] = "REQUIRED"
                props["oracle.net.encryption_types_client"] = "( $algorithm )"
            }
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
