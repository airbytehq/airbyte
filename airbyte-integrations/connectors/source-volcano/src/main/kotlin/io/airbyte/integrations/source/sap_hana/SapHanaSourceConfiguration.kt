/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.File
import java.io.FileOutputStream
import java.io.StringReader
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.security.KeyStore
import java.security.cert.Certificate
import java.security.cert.CertificateFactory
import java.time.Duration
import java.util.UUID
import org.bouncycastle.util.io.pem.PemReader

private val log = KotlinLogging.logger {}

/** SAP HANA specific implementation of [SourceConfiguration] */
data class SapHanaSourceConfiguration(
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
) : JdbcSourceConfiguration {
    val cdc: CdcIncrementalConfiguration? = incremental as? CdcIncrementalConfiguration
    override val global: Boolean = false
    override val maxSnapshotReadDuration: Duration? = cdc?.initialLoadTimeout

    override fun isCdc(): Boolean {
        return cdc != null
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialLoadTimeout: Duration,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,
    RESET_SYNC,
}

@Singleton
class SapHanaSourceConfigurationFactory :
    SourceConfigurationFactory<
        SapHanaSourceConfigurationSpecification, SapHanaSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: SapHanaSourceConfigurationSpecification,
    ): SapHanaSourceConfiguration {
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
        if (encryption is SslCertificate) {
            val pemFileContents: String = encryption.sslCertificate
            val pemReader = PemReader(StringReader(pemFileContents))
            val certDer = pemReader.readPemObject().content
            val cf: CertificateFactory = CertificateFactory.getInstance("X.509")
            val cert: Certificate = cf.generateCertificate(certDer.inputStream())
            val keyStore = KeyStore.getInstance(KeyStore.getDefaultType())
            keyStore.load(null, null) // Initialize the KeyStore
            keyStore.setCertificateEntry("rds-root", cert)
            val keyStorePass: String = UUID.randomUUID().toString()
            val keyStoreFile: File = Files.createTempFile("clientkeystore_", ".jks").toFile()
            keyStoreFile.deleteOnExit()
            val fos = FileOutputStream(keyStoreFile)
            keyStore.store(fos, keyStorePass.toCharArray())
            fos.close()
            jdbcProperties["javax.net.ssl.trustStore"] = keyStoreFile.toString()
            jdbcProperties["javax.net.ssl.trustStoreType"] = "JKS"
            jdbcProperties["javax.net.ssl.trustStorePassword"] = keyStorePass
        } else if (encryption is EncryptionAlgorithm) {
            // val algorithm: String = encryption.encryptionAlgorithm
            // TODO: use this field.
        }
        // val protocol: String = if (encryption is SslCertificate) "TCPS" else "TCP"
        // Build JDBC URL
        // val address = "(ADDRESS=(PROTOCOL=$protocol)(HOST=%s)(PORT=%d))"
        val jdbcUrlFmt = "jdbc:sap://%s:%s"

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
                    )
            }
        return SapHanaSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            defaultSchema = defaultSchema,
            namespaces = pojo.schemas?.toSet() ?: setOf(defaultSchema),
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
            incremental = incrementalConfiguration,
        )
    }
}
