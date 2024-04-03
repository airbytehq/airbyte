/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.ConnectorConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.ConnectorConfigurationSupplier
import io.airbyte.cdk.command.SourceConnectorConfiguration
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.io.IOs
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.File
import java.io.FileOutputStream
import java.io.StringReader
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.security.KeyStore
import java.security.cert.Certificate
import java.security.cert.CertificateFactory
import org.apache.commons.lang3.RandomStringUtils
import org.bouncycastle.util.io.pem.PemReader

private val logger = KotlinLogging.logger {}

/** Oracle-specific implementation of [SourceConnectorConfiguration] */
data class OracleSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    val defaultSchema: String,
    override val schemas: List<String>
) : SourceConnectorConfiguration {

    override val expectedStateType = AirbyteStateMessage.AirbyteStateType.STREAM
}

/** Factory for [OracleSourceConfiguration] using [OracleSourceConfigurationJsonObject]. */
@Singleton
private class OracleSourceConfigurationSupplierImpl (
    jsonObjectSupplier: ConnectorConfigurationJsonObjectSupplier<OracleSourceConfigurationJsonObject>
) : ConnectorConfigurationSupplier<OracleSourceConfiguration> {

    val value: OracleSourceConfiguration by lazy {
        val pojo: OracleSourceConfigurationJsonObject = jsonObjectSupplier.get()
        try {
            build(pojo)
        } catch (e: Exception) {
            // Wrap NPEs (mostly) in ConfigErrorException.
            throw ConfigErrorException("Failed to build OracleSourceConfiguration", e)
        }
    }

    override fun get(): OracleSourceConfiguration = value
}

private fun build(pojo: OracleSourceConfigurationJsonObject): OracleSourceConfiguration {
    val realHost: String = pojo.host!!
    val realPort: Int = pojo.port!!
    val sshTunnel: SshTunnelMethodConfiguration = pojo.getTunnelMethodValue()
    val jdbcProperties = mutableMapOf<String, String>()
    jdbcProperties["user"] = pojo.username!!
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
            logger.warn { "ignoring invalid JDBC URL param '$pair'" }
        } else {
            val key: String = result.groupValues[1].trim()
            val urlEncodedValue: String = result.groupValues[2].trim()
            jdbcProperties[key] = URLDecoder.decode(urlEncodedValue, StandardCharsets.UTF_8)
        }
    }
    // Determine protocol and configure encryption.
    val encryption: Encryption = pojo.getEncryptionValue()
    if (encryption is SslCertificate) {
        val pemFileContents: String = encryption.sslCertificate!!
        val pemReader = PemReader(StringReader(pemFileContents))
        val certDer = pemReader.readPemObject().content
        val cf: CertificateFactory = CertificateFactory.getInstance("X.509")
        val cert: Certificate = cf.generateCertificate(certDer.inputStream())
        val keyStore = KeyStore.getInstance(KeyStore.getDefaultType())
        keyStore.load(null, null) // Initialize the KeyStore
        keyStore.setCertificateEntry("rds-root", cert)
        val keyStorePass: String = RandomStringUtils.randomAlphanumeric(8)
        val keyStoreFile = File(IOs.writeFileToRandomTmpDir("clientkeystore.jks", ""))
        keyStoreFile.deleteOnExit()
        val fos = FileOutputStream(keyStoreFile)
        keyStore.store(fos, keyStorePass.toCharArray())
        fos.close()
        jdbcProperties["javax.net.ssl.trustStore"] = keyStoreFile.toString()
        jdbcProperties["javax.net.ssl.trustStoreType"] = "JKS"
        jdbcProperties["javax.net.ssl.trustStorePassword"] = keyStorePass
    } else if (encryption is EncryptionAlgorithm) {
        val algorithm: String = encryption.encryptionAlgorithm!!
        jdbcProperties["oracle.net.encryption_client"] = "REQUIRED"
        jdbcProperties["oracle.net.encryption_types_client"] = "( $algorithm )"
    }
    val protocol: String = if (encryption is SslCertificate) "TCPS" else "TCP"
    // Build JDBC URL
    val address = "(ADDRESS=(PROTOCOL=${protocol})(HOST=%s)(PORT=%d))"
    val connectionData: ConnectionData = pojo.getConnectionDataValue()
    val (connectDataType: String, connectDataValue: String) =
        when (connectionData) {
            is ServiceName -> "SERVICE_NAME" to connectionData.serviceName!!
            is Sid -> "SID" to connectionData.sid!!
        }
    val connectData = "(CONNECT_DATA=($connectDataType=$connectDataValue))"
    val jdbcUrlFmt = "jdbc:oracle:thin:@(DESCRIPTION=${address}${connectData})"
    val defaultSchema: String = pojo.username!!.uppercase()
    val sshOpts =
        SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())
    return OracleSourceConfiguration(
        realHost = realHost,
        realPort = realPort,
        sshTunnel = sshTunnel,
        sshConnectionOptions = sshOpts,
        jdbcUrlFmt = jdbcUrlFmt,
        jdbcProperties = jdbcProperties,
        defaultSchema = defaultSchema,
        schemas = pojo.schemas.ifEmpty { listOf(defaultSchema) },
    )
}
