/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.check

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class CloudHostCheckTest {

    private val cloud: Set<FeatureFlag> = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
    private val notCloud: Set<FeatureFlag> = emptySet()

    private val keyTunnel: SshTunnelMethodConfiguration =
        SshKeyAuthTunnelMethod(
            "bastion.example.com",
            22,
            "airbyte",
            "-----BEGIN RSA PRIVATE KEY-----",
        )
    private val passwordTunnel: SshTunnelMethodConfiguration =
        SshPasswordAuthTunnelMethod("bastion.example.com", 22, "airbyte", "secret")

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "localhost",
                "LOCALHOST",
                "  localhost  ",
                "127.0.0.1",
                "127.1.2.3",
                "127.255.255.255",
                "0.0.0.0",
                "::1",
                "[::1]",
                "0:0:0:0:0:0:0:1",
                "::",
                "[::]",
                "::ffff:127.0.0.1",
            ],
    )
    fun testLocalHostWithoutTunnelOnCloudIsRejected(host: String) {
        assertRejected(CloudHostCheck.LOCAL_HOST_MESSAGE, host, SshNoTunnelMethod, cloud)
        assertRejected(CloudHostCheck.LOCAL_HOST_MESSAGE, host, null, cloud)
    }

    @ParameterizedTest
    @ValueSource(strings = ["localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]"])
    fun testLocalHostWithTunnelOnCloudIsAccepted(host: String) {
        assertAccepted(host, keyTunnel, cloud)
        assertAccepted(host, passwordTunnel, cloud)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "postgres://user@host:5432/db",
                "jdbc:mysql://host:3306/db",
                "https://host",
                "https://host/",
                "host/db",
                "/host",
                "user@host",
                "user:password@host",
                "host:5432",
                "host:",
                " host:5432 ",
                "localhost:5432",
                "127.0.0.1:5432",
                "[::1]:5432",
                "[2001:db8::1]:5432",
                "[2001:db8::1]:",
            ],
    )
    fun testHostWithExtraSyntaxOnCloudIsRejected(host: String) {
        // The syntax message does not depend on the tunnel: the field content is wrong either way.
        assertRejected(CloudHostCheck.HOST_SYNTAX_MESSAGE, host, SshNoTunnelMethod, cloud)
        assertRejected(CloudHostCheck.HOST_SYNTAX_MESSAGE, host, keyTunnel, cloud)
        assertRejected(CloudHostCheck.HOST_SYNTAX_MESSAGE, host, null, cloud)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "db.example.com",
                " db.example.com ",
                "my-host",
                "10.0.0.5",
                "192.168.1.1",
                "128.0.0.1",
                "2001:db8::1",
                "[2001:db8::1]",
                "fe80::1",
                "0:0:0:0:0:0:0:2",
                "::ffff:10.0.0.5",
                "xyz:abc:def",
                "",
            ],
    )
    fun testReachableHostOnCloudIsAccepted(host: String) {
        assertAccepted(host, SshNoTunnelMethod, cloud)
        assertAccepted(host, null, cloud)
        assertAccepted(host, keyTunnel, cloud)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "localhost",
                "127.0.0.1",
                "0.0.0.0",
                "::1",
                "[::1]",
                "postgres://user@host:5432/db",
                "user@host",
                "host/db",
                "host:5432",
                "localhost:5432",
                "[::1]:5432",
            ],
    )
    fun testEverythingIsAcceptedOutsideCloud(host: String) {
        assertAccepted(host, SshNoTunnelMethod, notCloud)
        assertAccepted(host, null, notCloud)
        assertAccepted(host, keyTunnel, notCloud)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "https://acct.snowflakecomputing.com",
                "https://acct.snowflakecomputing.com/",
                "jdbc:snowflake://acct.snowflakecomputing.com",
                "acct.snowflakecomputing.com/console",
                "user@acct.snowflakecomputing.com",
                "acct.snowflakecomputing.com:443",
                " https://acct.snowflakecomputing.com ",
                "postgres://user@localhost:5432/db",
            ],
    )
    fun testSyntaxOnlyCheckRejectsExtraSyntaxOnCloud(host: String) {
        assertSyntaxRejected(CloudHostCheck.HOST_SYNTAX_MESSAGE, host, cloud, message = null)
        assertSyntaxRejected(CUSTOM_MESSAGE, host, cloud, message = CUSTOM_MESSAGE)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "acct.snowflakecomputing.com",
                " acct.snowflakecomputing.com ",
                "db.example.com",
                "10.0.0.5",
                "[2001:db8::1]",
                "",
                // No loopback check in the syntax-only variant.
                "localhost",
                "127.0.0.1",
                "0.0.0.0",
                "::1",
                "[::1]",
            ],
    )
    fun testSyntaxOnlyCheckAcceptsPlainHostOnCloud(host: String) {
        CloudHostCheck.validateHostSyntax(host, cloud)
        CloudHostCheck.validateHostSyntax(host, cloud, CUSTOM_MESSAGE)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "https://acct.snowflakecomputing.com",
                "user@acct.snowflakecomputing.com",
                "acct.snowflakecomputing.com/console",
                "acct.snowflakecomputing.com:443",
                "localhost",
            ],
    )
    fun testSyntaxOnlyCheckAcceptsEverythingOutsideCloud(host: String) {
        CloudHostCheck.validateHostSyntax(host, notCloud)
        CloudHostCheck.validateHostSyntax(host, notCloud, CUSTOM_MESSAGE)
    }

    @Test
    fun testSyntaxMessageWinsOverLocalHostMessage() {
        // A loopback host with extra syntax: the user must first fix what is in the field.
        assertRejected(
            CloudHostCheck.HOST_SYNTAX_MESSAGE,
            "postgres://user@localhost:5432/db",
            SshNoTunnelMethod,
            cloud,
        )
    }

    private fun assertRejected(
        expectedMessage: String,
        host: String,
        sshTunnel: SshTunnelMethodConfiguration?,
        featureFlags: Set<FeatureFlag>,
    ) {
        val e: ConfigErrorException =
            assertThrows<ConfigErrorException>("host '$host'") {
                CloudHostCheck.validate(host, sshTunnel, featureFlags)
            }
        Assertions.assertEquals(expectedMessage, e.message, "host '$host'")
    }

    private fun assertAccepted(
        host: String,
        sshTunnel: SshTunnelMethodConfiguration?,
        featureFlags: Set<FeatureFlag>,
    ) {
        // Any exception fails the test; the parameterized test name already carries the host.
        CloudHostCheck.validate(host, sshTunnel, featureFlags)
    }

    /** [message] null exercises the default argument of [CloudHostCheck.validateHostSyntax]. */
    private fun assertSyntaxRejected(
        expectedMessage: String,
        host: String,
        featureFlags: Set<FeatureFlag>,
        message: String?,
    ) {
        val e: ConfigErrorException =
            assertThrows<ConfigErrorException>("host '$host'") {
                if (message == null) {
                    CloudHostCheck.validateHostSyntax(host, featureFlags)
                } else {
                    CloudHostCheck.validateHostSyntax(host, featureFlags, message)
                }
            }
        Assertions.assertEquals(expectedMessage, e.message, "host '$host'")
    }

    companion object {
        private const val CUSTOM_MESSAGE: String = "Enter only the host domain in Host."
    }
}
