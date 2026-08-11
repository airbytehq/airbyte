/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MsSqlServerSslConfigurationTest {

    @Test
    fun verifyCertificateUsesConfiguredHostWhenTunnelIsEnabled() {
        val pojo = baseVerifyCertificatePojo()
        pojo.tunnelMethodJson =
            SshPasswordAuthTunnelMethod("localhost", 2222, "sshuser", "sshpass")

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)

        Assertions.assertEquals(
            "server.database.windows.net",
            config.jdbcProperties["hostNameInCertificate"],
        )
    }

    @Test
    fun verifyCertificateDoesNotSetHostNameWithoutTunnel() {
        val config = MsSqlServerSourceConfigurationFactory().make(baseVerifyCertificatePojo())

        Assertions.assertFalse(config.jdbcProperties.containsKey("hostNameInCertificate"))
    }

    @Test
    fun verifyCertificatePreservesExplicitHostNameWhenTunnelIsEnabled() {
        val pojo = baseVerifyCertificatePojo()
        pojo.tunnelMethodJson =
            SshPasswordAuthTunnelMethod("localhost", 2222, "sshuser", "sshpass")
        (pojo.encryptionJson as SslVerifyCertificate).hostNameInCertificate =
            "custom.database.windows.net"

        val config = MsSqlServerSourceConfigurationFactory().make(pojo)

        Assertions.assertEquals(
            "custom.database.windows.net",
            config.jdbcProperties["hostNameInCertificate"],
        )
    }

    private fun baseVerifyCertificatePojo(): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerSourceConfigurationSpecification().also {
            it.host = "server.database.windows.net"
            it.port = 1433
            it.database = "master"
            it.username = "sa"
            it.password = "Password123!"
            it.encryptionJson = SslVerifyCertificate()
            it.replicationMethodJson = UserDefinedCursor()
        }
}
