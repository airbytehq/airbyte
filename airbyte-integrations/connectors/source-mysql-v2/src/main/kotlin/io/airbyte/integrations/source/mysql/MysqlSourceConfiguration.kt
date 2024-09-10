/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
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
    val cursorConfiguration: CursorConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
) : JdbcSourceConfiguration {
    override val global = cursorConfiguration is CdcCursor
}

@Singleton
class MysqlSourceConfigurationFactory :
    SourceConfigurationFactory<MysqlSourceConfigurationJsonObject, MysqlSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MysqlSourceConfigurationJsonObject,
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
        val sslMode = pojo.encryption.encryptionMethod
        val jdbcEncryptionBuilder = MysqlJdbcEncryption.Builder().setSslMode(sslMode)

        when (encryption) {
            is EncryptionPreferred,
            is EncryptionRequired -> Unit
            is SslVerifyCertificate -> {
                jdbcEncryptionBuilder.apply {
                    setCaCertificate(encryption.sslCertificate)
                    if (encryption.sslClientKey != null) setClientKey(encryption.sslClientKey!!)
                    if (encryption.sslClientCertificate != null)
                        setClientCertificate(encryption.sslClientCertificate!!)
                    if (encryption.sslClientPassword != null)
                        setClientKeyPassword(encryption.sslClientPassword!!)
                }
            }
            is SslVerifyIdentity -> {
                jdbcEncryptionBuilder.apply {
                    setCaCertificate(encryption.sslCertificate)
                    if (encryption.sslClientKey != null) setClientKey(encryption.sslClientKey!!)
                    if (encryption.sslClientCertificate != null)
                        setClientCertificate(encryption.sslClientCertificate!!)
                    if (encryption.sslClientPassword != null)
                        setClientKeyPassword(encryption.sslClientPassword!!)
                }
            }
        }
        val sslJdbcParameters = jdbcEncryptionBuilder.build().parseSSLConfig()
        jdbcProperties.putAll(sslJdbcParameters)

        // Build JDBC URL
        val address = "%s:%d"
        val jdbcUrlFmt = "jdbc:mysql://${address}"
        jdbcProperties["useCursorFetch"] = "true"
        jdbcProperties["sessionVariables"] = "autocommit=0"
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
        return MysqlSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            namespaces = pojo.schemas?.toSet() ?: setOf(defaultSchema),
            cursorConfiguration = pojo.getCursorConfigurationValue(),
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }
}
