/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

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

/** Oracle-specific implementation of [SourceConfiguration] */
data class OracleSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    val defaultSchema: String,
    override val schemas: Set<String>,
    val cursorConfiguration: CursorConfiguration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    override val checkPrivileges: Boolean,
) : JdbcSourceConfiguration {
    override val global = cursorConfiguration is CdcCursor
}

@Singleton
class OracleSourceConfigurationFactory :
    SourceConfigurationFactory<OracleSourceConfigurationJsonObject, OracleSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: OracleSourceConfigurationJsonObject,
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
            val algorithm: String = encryption.encryptionAlgorithm
            jdbcProperties["oracle.net.encryption_client"] = "REQUIRED"
            jdbcProperties["oracle.net.encryption_types_client"] = "( $algorithm )"
        }
        val protocol: String = if (encryption is SslCertificate) "TCPS" else "TCP"
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
        return OracleSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = sshTunnel,
            sshConnectionOptions = sshOpts,
            jdbcUrlFmt = jdbcUrlFmt,
            jdbcProperties = jdbcProperties,
            defaultSchema = defaultSchema,
            schemas = pojo.schemas?.toSet() ?: setOf(defaultSchema),
            cursorConfiguration = pojo.getCursorConfigurationValue(),
            checkpointTargetInterval = checkpointTargetInterval,
            maxConcurrency = maxConcurrency,
            checkPrivileges = pojo.checkPrivileges ?: true,
        )
    }
}
