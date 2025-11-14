/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CdcSourceConfiguration
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.command.TableFilter
import io.airbyte.cdk.jdbc.SSLCertificateUtils
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
import java.net.MalformedURLException
import java.net.URI
import java.net.URL
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.nio.file.FileSystems
import java.time.Duration
import java.util.UUID

private val log = KotlinLogging.logger {}

/** MySQL-specific implementation of [SourceConfiguration] */
data class MySqlSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    override val tableFilters: List<TableFilter>,
    val incrementalConfiguration: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
    val debeziumKeepAliveInterval: Duration = Duration.ofMinutes(1),
) : JdbcSourceConfiguration, CdcSourceConfiguration {
    override val global = incrementalConfiguration is CdcIncrementalConfiguration
    override val maxSnapshotReadDuration: Duration?
        get() = (incrementalConfiguration as? CdcIncrementalConfiguration)?.initialLoadTimeout

    /** Required to inject [MySqlSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun mysqlSourceConfig(
            factory:
                SourceConfigurationFactory<
                    MySqlSourceConfigurationSpecification, MySqlSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<MySqlSourceConfigurationSpecification>,
        ): MySqlSourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialLoadTimeout: Duration,
    val serverTimezone: String?,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,
    RESET_SYNC,
}

@Singleton
class MySqlSourceConfigurationFactory
@Inject
constructor(
    val featureFlags: Set<FeatureFlag>,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
) : SourceConfigurationFactory<MySqlSourceConfigurationSpecification, MySqlSourceConfiguration> {

    constructor() : this(emptySet(), STDIO.name, emptyList())

    override fun makeWithoutExceptionHandling(
        pojo: MySqlSourceConfigurationSpecification,
    ): MySqlSourceConfiguration {
        val realHost: String = pojo.host
        val realPort: Int = pojo.port
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

        // Configure SSH tunneling.
        val sshTunnel: SshTunnelMethodConfiguration? = pojo.getTunnelMethodValue()
        val sshOpts: SshConnectionOptions =
            SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())

        // Configure SSL encryption.
        if (
            pojo.getEncryptionValue() is EncryptionPreferred &&
                sshTunnel is SshNoTunnelMethod &&
                featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
        ) {
            throw ConfigErrorException(
                "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel."
            )
        }
        val sslJdbcProperties: Map<String, String> = fromEncryptionSpec(pojo.getEncryptionValue()!!)
        jdbcProperties.putAll(sslJdbcProperties)
        log.info { "SSL mode: ${sslJdbcProperties["sslMode"]}" }

        // Configure cursor.
        val incremental: IncrementalConfiguration = fromIncrementalSpec(pojo.getIncrementalValue())

        // Build JDBC URL.
        val address = "%s:%d"
        val jdbcUrlFmt = "jdbc:mysql://${address}"
        jdbcProperties["useCursorFetch"] = "true"
        jdbcProperties["sessionVariables"] = "autocommit=0"

        // Only validate table filters if schemas are explicitly configured
        val tableFilters = pojo.tableFilters ?: emptyList()

        // Convert MySQL TableFilter to JDBC TableFilter for validation
        val jdbcTableFilters: List<TableFilter> =
            tableFilters.map {
                TableFilter().apply {
                    schemaName = it.databaseName
                    patterns = it.patterns
                }
            }

        pojo.database.let { schema ->
            JdbcSourceConfiguration.validateTableFilters(setOf(schema), jdbcTableFilters)
        }

        // Internal configuration settings.
        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 0)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }
        val maxConcurrencyLegacy: Int = pojo.concurrency ?: 0
        if ((pojo.concurrency ?: 0) <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }

        val maxDBConnections: Int? = pojo.max_db_connections

        log.info {
            "maxConcurrencyLegacy: $maxConcurrencyLegacy. maxDBConnections: $maxDBConnections. socket paths: ${socketPaths.size}"
        }

        // In legacy mode (STDIO), maxConcurrency is taken from the new setting max_db_connections
        // if set,
        // otherwise from the old concurrency setting.
        // Unless the users did something special, most will have concurrency = 1 in legacy mode.
        // In SOCKET mode, if max_db_connections is set, we use it.
        // Otherwise, if legacy concurrency is set to something other than the default 1, we use it.
        // Otherwise, we use the number of socket paths provided.
        // Most users run with concurrency = num_sockets in SOCKET mode.
        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> maxDBConnections ?: maxConcurrencyLegacy
                SOCKET -> {
                    maxDBConnections ?: maxConcurrencyLegacy.takeIf { it != 1 } ?: socketPaths.size
                }
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        return MySqlSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            namespaces = setOf(pojo.database),
            tableFilters = jdbcTableFilters,
            incrementalConfiguration = incremental,
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }

    private fun fromIncrementalSpec(
        incrementalSpec: IncrementalConfigurationSpecification
    ): IncrementalConfiguration =
        when (incrementalSpec) {
            UserDefinedCursor -> UserDefinedCursorIncrementalConfiguration
            is Cdc -> {
                val initialLoadTimeout: Duration =
                    Duration.ofHours(incrementalSpec.initialLoadTimeoutHours!!.toLong())
                val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior =
                    if (incrementalSpec.invalidCdcCursorPositionBehavior == "Fail sync") {
                        InvalidCdcCursorPositionBehavior.FAIL_SYNC
                    } else {
                        InvalidCdcCursorPositionBehavior.RESET_SYNC
                    }
                CdcIncrementalConfiguration(
                    initialLoadTimeout,
                    incrementalSpec.serverTimezone,
                    invalidCdcCursorPositionBehavior,
                )
            }
        }

    private fun fromEncryptionSpec(encryptionSpec: EncryptionSpecification): Map<String, String> {
        val extraJdbcProperties: MutableMap<String, String> = mutableMapOf()
        val sslData: SslData =
            when (encryptionSpec) {
                is EncryptionPreferred -> SslData("preferred")
                is EncryptionRequired -> SslData("required")
                is SslVerifyCertificate ->
                    SslData(
                        mode = "verify_ca",
                        caCertificate = encryptionSpec.sslCertificate,
                        clientCertificate = encryptionSpec.sslClientCertificate,
                        clientKey = encryptionSpec.sslClientKey,
                        keyStorePassword = encryptionSpec.sslClientPassword,
                    )
                is SslVerifyIdentity ->
                    SslData(
                        mode = "verify_identity",
                        caCertificate = encryptionSpec.sslCertificate,
                        clientCertificate = encryptionSpec.sslClientCertificate,
                        clientKey = encryptionSpec.sslClientKey,
                        keyStorePassword = encryptionSpec.sslClientPassword,
                    )
            }
        extraJdbcProperties[SSL_MODE] = sslData.mode
        if (sslData.caCertificate.isNullOrBlank()) {
            // if CA cert is not available - done
            return extraJdbcProperties
        }
        val password: String =
            sslData.keyStorePassword.takeUnless { it.isNullOrBlank() }
                ?: UUID.randomUUID().toString()
        // Make keystore for CA cert with given password or generate a new password.
        val caCertKeyStoreUrl: URL =
            buildKeyStore("trust") {
                SSLCertificateUtils.keyStoreFromCertificate(
                    sslData.caCertificate,
                    password,
                    FileSystems.getDefault(),
                    directory = "",
                )
            }
        extraJdbcProperties[TRUST_KEY_STORE_URL] = caCertKeyStoreUrl.toString()
        extraJdbcProperties[TRUST_KEY_STORE_PASS] = password
        extraJdbcProperties[TRUST_KEY_STORE_TYPE] = KEY_STORE_TYPE_PKCS12

        if (sslData.clientCertificate.isNullOrBlank() || sslData.clientKey.isNullOrBlank()) {
            // if Client cert is not available - done
            return extraJdbcProperties
        }
        // Make keystore for Client cert with given password or generate a new password.
        val clientCertKeyStoreUrl: URL =
            buildKeyStore("client") {
                SSLCertificateUtils.keyStoreFromClientCertificate(
                    sslData.clientCertificate,
                    sslData.clientKey,
                    password,
                    directory = ""
                )
            }
        extraJdbcProperties[CLIENT_KEY_STORE_URL] = clientCertKeyStoreUrl.toString()
        extraJdbcProperties[CLIENT_KEY_STORE_PASS] = password
        extraJdbcProperties[CLIENT_KEY_STORE_TYPE] = KEY_STORE_TYPE_PKCS12
        return extraJdbcProperties
    }

    private data class SslData(
        val mode: String,
        val caCertificate: String? = null,
        val clientCertificate: String? = null,
        val clientKey: String? = null,
        val keyStorePassword: String? = null,
    )

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

    companion object {
        const val TRUST_KEY_STORE_URL: String = "trustCertificateKeyStoreUrl"
        const val TRUST_KEY_STORE_PASS: String = "trustCertificateKeyStorePassword"
        const val CLIENT_KEY_STORE_URL: String = "clientCertificateKeyStoreUrl"
        const val CLIENT_KEY_STORE_PASS: String = "clientCertificateKeyStorePassword"
        const val CLIENT_KEY_STORE_TYPE: String = "clientCertificateKeyStoreType"
        const val TRUST_KEY_STORE_TYPE: String = "trustCertificateKeyStoreType"
        const val KEY_STORE_TYPE_PKCS12: String = "PKCS12"
        const val SSL_MODE: String = "sslMode"
    }
}
