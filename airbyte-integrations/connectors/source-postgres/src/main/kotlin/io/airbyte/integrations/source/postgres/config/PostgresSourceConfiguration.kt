/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.config

import com.azure.core.credential.AccessToken
import com.azure.core.credential.TokenRequestContext
import com.azure.identity.ClientSecretCredentialBuilder
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CdcSourceConfiguration
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
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
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import java.time.Duration
import java.util.*
import org.postgresql.PGProperty.CONNECT_TIMEOUT
import org.postgresql.PGProperty.PREPARE_THRESHOLD
import org.postgresql.PGProperty.TCP_KEEP_ALIVE
import org.postgresql.jdbc.SslMode.ALLOW
import org.postgresql.jdbc.SslMode.DISABLE
import org.postgresql.jdbc.SslMode.PREFER
import org.postgresql.jdbc.SslMode.REQUIRE
import org.postgresql.jdbc.SslMode.VERIFY_CA
import org.postgresql.jdbc.SslMode.VERIFY_FULL

private val log = KotlinLogging.logger {}

/** Postgres-specific implementation of [SourceConfiguration] */
data class PostgresSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    val database: String,
    override val namespaces: Set<String>,
    val incrementalConfiguration: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
) : JdbcSourceConfiguration, CdcSourceConfiguration {
    val cdc: CdcIncrementalConfiguration? = incrementalConfiguration as? CdcIncrementalConfiguration

    override val global: Boolean = cdc != null
    override val maxSnapshotReadDuration: Duration? = cdc?.initialLoadTimeout

    /** Required to inject [PostgresSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun postgresSourceConfig(
            factory:
                SourceConfigurationFactory<
                    PostgresSourceConfigurationSpecification,
                    PostgresSourceConfiguration,
                >,
            supplier: ConfigurationSpecificationSupplier<PostgresSourceConfigurationSpecification>
        ) = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data object XminIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialLoadTimeout: Duration,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
    val shutdownTimeout: Duration,
    val replicationSlot: String,
    val publication: String,
    val debeziumCommitsLsn: Boolean,
// TODO: Support this configuration:
//  initial waiting time in seconds
//  size of the queue
//  debezium heartbeat query
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,
    RESET_SYNC,
}

@Singleton
class PostgresSourceConfigurationFactory
@Inject
constructor(
    val featureFlags: Set<FeatureFlag>,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
) :
    SourceConfigurationFactory<
        PostgresSourceConfigurationSpecification,
        PostgresSourceConfiguration,
    > {

    constructor() : this(emptySet(), STDIO.name, emptyList())

    override fun makeWithoutExceptionHandling(
        pojo: PostgresSourceConfigurationSpecification,
    ): PostgresSourceConfiguration {
        val realHost: String = pojo.host
        val realPort: Int = pojo.port
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        passwordOrToken(pojo)?.let { jdbcProperties["password"] = it }

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
            pojo.getEncryptionValue() in
                listOf(EncryptionDisable, EncryptionAllow, EncryptionPrefer) &&
                sshTunnel is SshNoTunnelMethod &&
                featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
        ) {
            throw ConfigErrorException(
                "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel."
            )
        }

        val sslJdbcProperties: Map<String, String> = pojo.getEncryptionValue()!!.jdbcProperties()
        jdbcProperties.putAll(sslJdbcProperties)
        log.info { "SSL mode: ${sslJdbcProperties["sslmode"]}" }

        applyDefaultJdbcProperties(jdbcProperties)

        // Configure cursor.
        val incremental: IncrementalConfiguration =
            fromIncrementalSpec(pojo.getIncrementalConfigurationSpecificationValue())

        var encodedDatabaseName = URLEncoder.encode(pojo.database, StandardCharsets.UTF_8.name())

        // Build JDBC URL.
        val jdbcUrlFmt = "jdbc:postgresql://%s:%d/$encodedDatabaseName"

        // Internal configuration settings.
        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 0)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }

        // TODO: only use username from <username>@azure.com when checking privileges

        val maxDBConnections: Int? = pojo.max_db_connections

        log.info { "maxDBConnections: $maxDBConnections. socket paths: ${socketPaths.size}" }

        // If max_db_connections is set, we use it.
        // Otherwise, we use the number of socket paths provided for speed mode
        // Or 1 for legacy mode
        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> maxDBConnections ?: 1
                SOCKET -> maxDBConnections ?: socketPaths.size
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        val namespaces: Set<String> =
            pojo.schemas?.filter { it.isNotBlank() }?.toSet()?.takeUnless { it.isEmpty() }
                ?: setOf("public")

        return PostgresSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            database = pojo.database,
            namespaces = namespaces,
            incrementalConfiguration = incremental,
            maxConcurrency = maxConcurrency,
            checkpointTargetInterval = checkpointTargetInterval,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }

    private fun applyDefaultJdbcProperties(jdbcProperties: MutableMap<String, String>) {
        jdbcProperties.putIfAbsent(
            CONNECT_TIMEOUT.getName(),
            CONNECT_TIMEOUT.defaultValue.toString()
        )
        jdbcProperties.putIfAbsent(PREPARE_THRESHOLD.getName(), "0")
        jdbcProperties.putIfAbsent(TCP_KEEP_ALIVE.getName(), "true")
    }

    private fun fromIncrementalSpec(
        incrementalSpec: IncrementalConfigurationSpecification
    ): IncrementalConfiguration =
        when (incrementalSpec) {
            StandardReplicationMethodConfigurationSpecification ->
                UserDefinedCursorIncrementalConfiguration
            XminReplicationMethodConfigurationSpecification -> XminIncrementalConfiguration
            is CdcReplicationMethodConfigurationSpecification -> {
                val initialLoadTimeout: Duration =
                    Duration.ofHours(incrementalSpec.initialLoadTimeoutHours!!.toLong())
                val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior =
                    if (incrementalSpec.invalidCdcCursorPositionBehavior == "Fail sync") {
                        InvalidCdcCursorPositionBehavior.FAIL_SYNC
                    } else {
                        InvalidCdcCursorPositionBehavior.RESET_SYNC
                    }
                val shutdownTimeout: Duration =
                    Duration.ofSeconds(incrementalSpec.debeziumShutdownTimeoutSeconds!!.toLong())
                CdcIncrementalConfiguration(
                    initialLoadTimeout = initialLoadTimeout,
                    invalidCdcCursorPositionBehavior = invalidCdcCursorPositionBehavior,
                    shutdownTimeout = shutdownTimeout,
                    replicationSlot = incrementalSpec.replicationSlot,
                    publication = incrementalSpec.publication,
                    debeziumCommitsLsn = incrementalSpec.lsnCommitBehavior == "While reading Data",
                )
            }
        }

    private fun EncryptionSpecification.jdbcProperties(): Map<String, String> {
        //    private fun fromEncryptionSpec(encryptionSpec: EncryptionSpecification): Map<String,
        // String> {
        val extraJdbcProperties: MutableMap<String, String> = mutableMapOf()
        val sslData: SslData =
            when (this) {
                is EncryptionDisable -> SslData(DISABLE.value)
                is EncryptionAllow -> SslData(ALLOW.value)
                is EncryptionPrefer -> SslData(PREFER.value)
                is EncryptionRequire -> SslData(REQUIRE.value)
                is SslVerifyCertificate ->
                    SslData(
                        mode = VERIFY_CA.value,
                        caCertificate = sslCertificate,
                        clientCertificate = sslClientCertificate,
                        clientKey = sslClientKey,
                        keyStorePassword = sslClientPassword,
                    )
                is SslVerifyFull ->
                    SslData(
                        mode = VERIFY_FULL.value,
                        caCertificate = sslCertificate,
                        clientCertificate = sslClientCertificate,
                        clientKey = sslClientKey,
                        keyStorePassword = sslClientPassword,
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

        extraJdbcProperties[CLIENT_KEY_STORE_PASS] = password
        // Save CA certificate to a temporary file
        val caCertFileURI: URI = saveCACertificate {
            val caCertFile = Files.createTempFile(null, null)
            Files.write(caCertFile, sslData.caCertificate.toByteArray(StandardCharsets.UTF_8))
                .also { it.toFile().deleteOnExit() }
        }
        extraJdbcProperties[TRUST_KEY_STORE_URL] = Paths.get(caCertFileURI).toString()

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
        extraJdbcProperties[CLIENT_KEY_STORE_URL] =
            Paths.get(clientCertKeyStoreUrl.toURI()).toString()
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

    private fun saveCACertificate(uriSupplier: () -> Path): URI {
        val caCertPath: Path =
            try {
                uriSupplier()
            } catch (ex: Exception) {
                throw ConfigErrorException("Failed to create CA certificate file", ex)
            }
        val caCertUrl: URI =
            try {
                caCertPath.toUri()
            } catch (ex: MalformedURLException) {
                throw ConfigErrorException("Unable to get a URI for certificate file", ex)
            }
        log.debug { "URI for certificate file is $caCertUrl" }
        return caCertUrl
    }

    // Debug functions to validate encryption functionality
    /*private fun validateCertificateFile(certPath: String, kind: String) {
        try {
            val certFile = File(certPath)
            if (!certFile.exists()) {
                throw ConfigErrorException("$kind file not found at: $certPath")
            }

            if (!certFile.canRead()) {
                throw ConfigErrorException("$kind file is not readable at: $certPath")
            }

            // Read and validate the PEM certificate
            val certContent = certFile.readText()
            if (!certContent.contains("BEGIN CERTIFICATE")) {
                throw ConfigErrorException("$kind file does not appear to be a valid PEM certificate at: $certPath")
            }

            // Try to parse the certificate to ensure it's valid
            val certificateFactory = java.security.cert.CertificateFactory.getInstance("X.509")
            certFile.inputStream().use { fis ->
                val cert = certificateFactory.generateCertificate(fis) as java.security.cert.X509Certificate
                log.info { "$kind validated successfully at $certPath" }
                log.debug { "  Subject: ${cert.subjectX500Principal}" }
                log.debug { "  Issuer: ${cert.issuerX500Principal}" }
                log.debug { "  Valid from: ${cert.notBefore} to: ${cert.notAfter}" }
            }

        } catch (ex: java.security.cert.CertificateException) {
            throw ConfigErrorException("Invalid $kind format at $certPath", ex)
        } catch (ex: java.io.IOException) {
            throw ConfigErrorException("Failed to read $kind at $certPath", ex)
        }
    }

    private fun validateKeyStore(keystorePath: String, password: String?, kind: String) {
        try {
            val keystoreFile = File(keystorePath)
            if (!keystoreFile.exists()) {
                throw ConfigErrorException("$kind keystore file not found at: $keystorePath")
            }

            if (!keystoreFile.canRead()) {
                throw ConfigErrorException("$kind keystore file is not readable at: $keystorePath")
            }

            // Load and validate the PKCS12 keystore
            val keyStore = java.security.KeyStore.getInstance("PKCS12")
            keystoreFile.inputStream().use { fis ->
                keyStore.load(fis, password?.toCharArray())
            }

            // Log keystore contents for debugging
            val aliases = keyStore.aliases().toList()
            log.info { "$kind keystore validated successfully at $keystorePath with ${aliases.size} entries" }

            aliases.forEach { alias ->
                val isCertificate = keyStore.isCertificateEntry(alias)
                val isKey = keyStore.isKeyEntry(alias)
                log.debug { "  Alias: $alias, isCertificate: $isCertificate, isKey: $isKey" }

                if (isCertificate) {
                    val cert = keyStore.getCertificate(alias)
                    log.debug { "  Certificate type: ${cert.type}" }
                }
            }

            if (aliases.isEmpty()) {
                log.warn { "$kind keystore at $keystorePath contains no entries" }
            }

        } catch (ex: java.security.KeyStoreException) {
            throw ConfigErrorException("Invalid $kind keystore format at $keystorePath", ex)
        } catch (ex: java.security.cert.CertificateException) {
            throw ConfigErrorException("Invalid certificate in $kind keystore at $keystorePath", ex)
        } catch (ex: java.security.NoSuchAlgorithmException) {
            throw ConfigErrorException("Unsupported algorithm in $kind keystore at $keystorePath", ex)
        } catch (ex: java.io.IOException) {
            if (ex.cause is java.security.UnrecoverableKeyException ||
                ex.message?.contains("password", ignoreCase = true) == true) {
                throw ConfigErrorException("Incorrect password for $kind keystore at $keystorePath", ex)
            }
            throw ConfigErrorException("Failed to read $kind keystore at $keystorePath", ex)
        }
    }*/

    companion object {
        const val TRUST_KEY_STORE_URL: String = "sslrootcert"
        const val CLIENT_KEY_STORE_URL: String = "sslkey"
        const val CLIENT_KEY_STORE_PASS: String = "sslpassword"
        const val SSL_MODE: String = "sslmode"
    }

    private fun passwordOrToken(pojo: PostgresSourceConfigurationSpecification): String? {
        if (pojo.servicePrincipalAuth) {
            val credential =
                ClientSecretCredentialBuilder()
                    .clientId(pojo.clientId)
                    .clientSecret(pojo.password)
                    .tenantId(pojo.tenantId)
                    .build()

            val tokenRequestContext =
                TokenRequestContext()
                    .addScopes("https://ossrdbms-aad.database.windows.net/.default")

            val accessToken: AccessToken =
                credential.getToken(tokenRequestContext).retry(3L).blockOptional().orElseThrow {
                    RuntimeException("Failed to retrieve token for Entra service principal")
                }

            return accessToken.token
        } else return pojo.password
    }
}
