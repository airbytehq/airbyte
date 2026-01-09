/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.jdbc.SSLCertificateUtils
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.net.MalformedURLException
import java.net.URI
import java.net.URL
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.nio.file.FileSystems
import java.time.Duration
import java.util.UUID

private val log = KotlinLogging.logger {}

/** PostgreSQL V2-specific implementation of [JdbcSourceConfiguration] */
data class PostgresV2SourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    val incrementalConfiguration: PostgresV2IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val maxSnapshotReadDuration: Duration? = null,
) : JdbcSourceConfiguration {
    override val global = false

    /** Required to inject [PostgresV2SourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun postgresV2SourceConfig(
            factory:
                SourceConfigurationFactory<
                    PostgresV2SourceConfigurationSpecification, PostgresV2SourceConfiguration>,
            supplier:
                ConfigurationSpecificationSupplier<PostgresV2SourceConfigurationSpecification>,
        ): PostgresV2SourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface PostgresV2IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : PostgresV2IncrementalConfiguration

data object XminIncrementalConfiguration : PostgresV2IncrementalConfiguration

@Singleton
class PostgresV2SourceConfigurationFactory :
    SourceConfigurationFactory<
        PostgresV2SourceConfigurationSpecification, PostgresV2SourceConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: PostgresV2SourceConfigurationSpecification,
    ): PostgresV2SourceConfiguration {
        val realHost: String = pojo.host
        val realPort: Int = pojo.port
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }

        // Parse URL parameters
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

        // Configure SSH tunneling
        val sshTunnel: SshTunnelMethodConfiguration? = pojo.getTunnelMethodValue()
        val sshOpts: SshConnectionOptions =
            SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())

        // Configure SSL encryption
        val sslJdbcProperties: Map<String, String> = fromSslModeSpec(pojo.getSslModeValue())
        jdbcProperties.putAll(sslJdbcProperties)
        log.info { "SSL mode: ${sslJdbcProperties["sslmode"]}" }

        // Configure incremental method
        val incremental: PostgresV2IncrementalConfiguration =
            fromIncrementalSpec(pojo.getIncrementalValue())

        // Build JDBC URL - %s:%d will be replaced with host:port by the framework
        val address = "%s:%d"
        val jdbcUrlFmt = "jdbc:postgresql://${address}/${pojo.database}"

        // Internal configuration settings
        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 300)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }
        val maxConcurrency: Int = pojo.concurrency ?: 1
        if (maxConcurrency <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }

        return PostgresV2SourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            namespaces = pojo.schemas.toSet(),
            incrementalConfiguration = incremental,
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
        )
    }

    private fun fromIncrementalSpec(
        incrementalSpec: IncrementalConfigurationSpecification
    ): PostgresV2IncrementalConfiguration =
        when (incrementalSpec) {
            UserDefinedCursor -> UserDefinedCursorIncrementalConfiguration
            Xmin -> XminIncrementalConfiguration
        }

    private fun fromSslModeSpec(sslModeSpec: SslModeSpecification?): Map<String, String> {
        val extraJdbcProperties: MutableMap<String, String> = mutableMapOf()
        when (sslModeSpec) {
            is SslModeDisable -> {
                extraJdbcProperties["sslmode"] = "disable"
            }
            is SslModeAllow -> {
                extraJdbcProperties["sslmode"] = "allow"
            }
            is SslModePrefer,
            null -> {
                extraJdbcProperties["sslmode"] = "prefer"
            }
            is SslModeRequire -> {
                extraJdbcProperties["sslmode"] = "require"
            }
            is SslModeVerifyCa -> {
                extraJdbcProperties["sslmode"] = "verify-ca"
                configureSslCertificates(
                    extraJdbcProperties,
                    sslModeSpec.caCertificate,
                    sslModeSpec.clientCertificate,
                    sslModeSpec.clientKey,
                    sslModeSpec.clientKeyPassword
                )
            }
            is SslModeVerifyFull -> {
                extraJdbcProperties["sslmode"] = "verify-full"
                configureSslCertificates(
                    extraJdbcProperties,
                    sslModeSpec.caCertificate,
                    sslModeSpec.clientCertificate,
                    sslModeSpec.clientKey,
                    sslModeSpec.clientKeyPassword
                )
            }
        }
        return extraJdbcProperties
    }

    private fun configureSslCertificates(
        jdbcProperties: MutableMap<String, String>,
        caCertificate: String,
        clientCertificate: String?,
        clientKey: String?,
        clientKeyPassword: String?,
    ) {
        val password: String =
            clientKeyPassword.takeUnless { it.isNullOrBlank() } ?: UUID.randomUUID().toString()

        // Create trust store for CA certificate
        val trustStoreUrl: URL =
            buildKeyStore("trust") {
                SSLCertificateUtils.keyStoreFromCertificate(
                    caCertificate,
                    password,
                    FileSystems.getDefault(),
                    directory = "",
                )
            }
        jdbcProperties["sslrootcert"] = trustStoreUrl.path

        if (!clientCertificate.isNullOrBlank() && !clientKey.isNullOrBlank()) {
            // Create key store for client certificate
            val clientKeyStoreUrl: URL =
                buildKeyStore("client") {
                    SSLCertificateUtils.keyStoreFromClientCertificate(
                        clientCertificate,
                        clientKey,
                        password,
                        directory = ""
                    )
                }
            jdbcProperties["sslcert"] = clientKeyStoreUrl.path
            jdbcProperties["sslkey"] = clientKey
            if (!clientKeyPassword.isNullOrBlank()) {
                jdbcProperties["sslpassword"] = clientKeyPassword
            }
        }
    }

    private fun buildKeyStore(kind: String, uriSupplier: () -> URI): URL {
        val keyStoreUri: URI =
            try {
                uriSupplier()
            } catch (ex: Exception) {
                throw ConfigErrorException("Failed to create keystore for $kind certificate", ex)
            }
        val keyStoreUrl: URL =
            try {
                keyStoreUri.toURL()
            } catch (ex: MalformedURLException) {
                throw ConfigErrorException("Unable to get a URL for $kind key store", ex)
            }
        log.debug { "URL for $kind certificate keystore is $keyStoreUrl" }
        return keyStoreUrl
    }
}
