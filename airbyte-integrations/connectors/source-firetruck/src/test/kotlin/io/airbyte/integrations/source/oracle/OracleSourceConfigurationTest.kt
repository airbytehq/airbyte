/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlin.time.Duration.Companion.ZERO
import kotlin.time.Duration.Companion.milliseconds
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class OracleSourceConfigurationTest {
    @Inject
    lateinit var pojoSupplier: ConfigurationJsonObjectSupplier<OracleSourceConfigurationJsonObject>

    @Inject
    lateinit var factory:
        SourceConfigurationFactory<OracleSourceConfigurationJsonObject, OracleSourceConfiguration>

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.schemas", value = "FOO")
    @Property(
        name = "airbyte.connector.config.connection_data.connection_type",
        value = "service_name",
    )
    @Property(name = "airbyte.connector.config.connection_data.service_name", value = "FREEPDB1")
    @Property(name = "airbyte.connector.config.encryption.encryption_method", value = "client_nne")
    @Property(name = "airbyte.connector.config.encryption.encryption_algorithm", value = "3DES168")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_method",
        value = "SSH_PASSWORD_AUTH",
    )
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_host", value = "localhost")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_port", value = "2222")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user", value = "sshuser")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user_password", value = "***")
    fun testWithEncryptionAlgorithm() {
        val conf: OracleSourceConfiguration = factory.make(pojoSupplier.get())
        Assertions.assertEquals("localhost", conf.realHost)
        Assertions.assertEquals(12345, conf.realPort)
        val expectedSsh = SshPasswordAuthTunnelMethod("localhost", 2222, "sshuser", "***")
        Assertions.assertEquals(expectedSsh, conf.sshTunnel)
        val expectedSshOpts = SshConnectionOptions(1_000.milliseconds, 2_000.milliseconds, ZERO)
        Assertions.assertEquals(expectedSshOpts, conf.sshConnectionOptions)
        val expectedUrl =
            "jdbc:oracle:thin:@(DESCRIPTION=" +
                "(ADDRESS=(PROTOCOL=TCP)(HOST=%s)(PORT=%d))" +
                "(CONNECT_DATA=(SERVICE_NAME=FREEPDB1)))"
        Assertions.assertEquals(expectedUrl, conf.jdbcUrlFmt)
        val expectedProperties =
            mapOf(
                "user" to "FOO",
                "password" to "BAR",
                "oracle.jdbc.useFetchSizeWithLongColumn" to "true",
                "oracle.net.encryption_client" to "REQUIRED",
                "oracle.net.encryption_types_client" to "( 3DES168 )",
            )
        Assertions.assertEquals(expectedProperties, conf.jdbcProperties)
        Assertions.assertEquals("FOO", conf.defaultSchema)
        Assertions.assertEquals(setOf("FOO"), conf.schemas)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.schemas", value = "FOO")
    @Property(name = "airbyte.connector.config.connection_data.connection_type", value = "sid")
    @Property(name = "airbyte.connector.config.connection_data.sid", value = "DB_SID")
    @Property(
        name = "airbyte.connector.config.encryption.encryption_method",
        value = "encrypted_verify_certificate",
    )
    @Property(name = "airbyte.connector.config.encryption.ssl_certificate", value = PEM_FILE)
    fun testWithValidSslCertificate() {
        val conf: OracleSourceConfiguration = factory.make(pojoSupplier.get())
        Assertions.assertEquals("localhost", conf.realHost)
        Assertions.assertEquals(12345, conf.realPort)
        Assertions.assertEquals(SshNoTunnelMethod, conf.sshTunnel)
        val expectedUrl =
            "jdbc:oracle:thin:@(DESCRIPTION=" +
                "(ADDRESS=(PROTOCOL=TCPS)(HOST=%s)(PORT=%d))" +
                "(CONNECT_DATA=(SID=DB_SID)))"
        Assertions.assertEquals(expectedUrl, conf.jdbcUrlFmt)
        Assertions.assertNotNull(conf.jdbcProperties["javax.net.ssl.trustStore"])
        Assertions.assertNotNull(conf.jdbcProperties["javax.net.ssl.trustStorePassword"])
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.schemas", value = "FOO")
    @Property(name = "airbyte.connector.config.connection_data.connection_type", value = "sid")
    @Property(name = "airbyte.connector.config.connection_data.sid", value = "DB_SID")
    @Property(
        name = "airbyte.connector.config.encryption.encryption_method",
        value = "encrypted_verify_certificate",
    )
    @Property(name = "airbyte.connector.config.encryption.ssl_certificate", value = "non-PEM trash")
    fun testWithInvalidSslCertificate() {
        val pojo: OracleSourceConfigurationJsonObject = pojoSupplier.get()
        Assertions.assertThrows(ConfigErrorException::class.java) { factory.make(pojo) }
    }
}

const val PEM_FILE =
    """
-----BEGIN CERTIFICATE-----
MIIDizCCAnOgAwIBAgIUVWCfGs+uSa8Kcuzj3d/IkYbYMCwwDQYJKoZIhvcNAQEL
BQAwVTELMAkGA1UEBhMCQ0ExCzAJBgNVBAgMAlFDMRYwFAYDVQQHDA1EcnVtbW9u
ZHZpbGxlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMjQw
NDA1MDMxNDA0WhcNMjUwNDA1MDMxNDA0WjBVMQswCQYDVQQGEwJDQTELMAkGA1UE
CAwCUUMxFjAUBgNVBAcMDURydW1tb25kdmlsbGUxITAfBgNVBAoMGEludGVybmV0
IFdpZGdpdHMgUHR5IEx0ZDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
AOW7ZXDcu27bT2HfyTkLZ1lwNKwVYLHirBorpdMWqlZucBqpflh9snijmapgEhkY
EXdWtNW2kp5isrRB/AgwwqepbPFrsZGM7U9XDMzmRDENFF3+R3zYouyEONAzVl+P
SJYmeRm6xIbz1+L/YXrtc4clRoQN9J1opmqMzeMi74ShHoBFVHyuJr1QZFC2otij
Gw9IaJ3IWNThaXm+Txits5cyMkAKbUSkNJs4tjtbPpkOJsvhvZiWvQFHtaH+Cm9M
i4bwnZlKCN/1Ubn40of/nsEsIQlzIfY90ydswPy68azxFDNFE22SxNw+gPF3sJ99
Y9T61IqNV1VLhQfEheo2mHUCAwEAAaNTMFEwHQYDVR0OBBYEFCmUa/lmXwJxFN5A
sRlVfzlcrs/uMB8GA1UdIwQYMBaAFCmUa/lmXwJxFN5AsRlVfzlcrs/uMA8GA1Ud
EwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAFVnpF91oNhkIMg3cIJCFCIi
WCtPdG9njY9S5zcH7S8ZsQyRiODRL7OEkqhT3frGWgjFiVHRNatuOyyra8KracpD
hjyRWw/FMTT2+2zhf7cKqdB5kwAiDTr/CGcV8pYqy1YVjrHJ0SbkD+1i2AXJg6ks
2NfdHiWiAG56+xygyu5k5kUpF2KAVQLK7oaIPsazP1aGiAckYKDNzt2to3dNq9B8
DCDug44eK1q3ciBAojpbVjJO/sRLyXl5EGsJv2fAOFCC9NrcBhWqFulktQVZu7Wd
kRj5zGaGRdL+l0Io1vHgJY7jNf3qp9F0uo4MIumj4CXRxq115zCbeznr0wr5/j0=
-----END CERTIFICATE-----
"""
