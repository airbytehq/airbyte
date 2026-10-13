/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ConnectorError
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.ConnectException
import java.net.UnknownHostException
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Exercises the regex rules in `src/main/resources/application.yml`. The same rule serves a failed
 * connection test (CHECK) and a failed sync, so the unreachable-host messages must point at the
 * host, port, firewall and the Airbyte Cloud IP allowlist, and must not promise a retry.
 */
@MicronautTest
class MsSqlServerExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testTcpIpConnectionRefusedIsUnreachableHost() {
        // The driver throws a SQLServerException whose message embeds the socket error and whose
        // cause is the java.net exception.
        val exception =
            SQLException(
                tcpIpConnectionFailed("Connection refused"),
                ConnectException("Connection refused")
            )
        assertUnreachableHost(classifier.classify(exception))
    }

    @Test
    fun testTcpIpConnectionTimedOutIsUnreachableHost() {
        val exception =
            SQLException(
                tcpIpConnectionFailed("connect timed out"),
                java.net.SocketTimeoutException("connect timed out"),
            )
        assertUnreachableHost(classifier.classify(exception))
    }

    @Test
    fun testUnknownHostIsUnreachableHost() {
        // java.net.UnknownHostException is folded into the TCP/IP message by the driver.
        val exception =
            SQLException(
                "The TCP/IP connection to the host nonexistent-host.invalid, port 1433 has failed. " +
                    "Error: \"nonexistent-host.invalid: System error. Verify the connection properties. " +
                    "Make sure that an instance of SQL Server is running on the host and accepting " +
                    "TCP/IP connections at the port. Make sure that TCP connections to the port are " +
                    "not blocked by a firewall.\".",
                UnknownHostException("nonexistent-host.invalid: System error"),
            )
        assertUnreachableHost(classifier.classify(exception))
    }

    @Test
    fun testLoginTimeoutExpiredIsUnreachableHostNotQueryTimeout() {
        val exception = SQLException("Login timeout expired.")
        val result = classifier.classify(exception)
        assertUnreachableHost(result)
        Assertions.assertFalse(
            (result as TransientError).displayMessage.contains("query took too long"),
            "Login timeout must not be classified as a query timeout: ${result.displayMessage}",
        )
    }

    @Test
    fun testTcpIpFailureNestedInChangeEventProducerIsUnreachableHost() {
        // CDC wraps driver failures in the Debezium "change event producer" exception; the
        // unreachable-host rule precedes the change event producer rule, so the nested cause wins.
        val driverException =
            SQLException(
                tcpIpConnectionFailed("Connection refused"),
                ConnectException("Connection refused")
            )
        val connectException =
            RuntimeException(
                "An exception occurred in the change event producer. This connector will be stopped.",
                driverException,
            )
        assertUnreachableHost(classifier.classify(connectException))
    }

    @Test
    fun testLoginFailedIsConfigErrorWithoutFirewallGuidance() {
        val exception = SQLException("Login failed for user 'sa'.")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        val displayMessage = (result as ConfigError).displayMessage
        Assertions.assertFalse(
            displayMessage.contains("firewall"),
            "Authentication errors must not get the unreachable-host guidance: $displayMessage",
        )
    }

    @Test
    fun testUnrelatedMessageIsNotClassified() {
        val exception = RuntimeException("Something unrelated happened while reading a row.")
        Assertions.assertNull(classifier.classify(exception))
    }

    private fun assertUnreachableHost(result: ConnectorError?) {
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val displayMessage = (result as TransientError).displayMessage
        Assertions.assertTrue(
            displayMessage.contains(
                "Airbyte could not reach SQL Server at the configured host and port"
            ),
            "Unexpected message: $displayMessage",
        )
        Assertions.assertTrue(
            displayMessage.contains("Check the host and port"),
            "Unexpected message: $displayMessage",
        )
        Assertions.assertTrue(
            displayMessage.contains(
                "your firewall or security group allows Airbyte's IP addresses"
            ),
            "Expected firewall / Airbyte IP guidance, got: $displayMessage",
        )
        Assertions.assertTrue(
            displayMessage.contains(
                "https://docs.airbyte.com/platform/operating-airbyte/security#ip-addresses"
            ),
            "Expected the Airbyte Cloud IP list link, got: $displayMessage",
        )
        Assertions.assertTrue(
            displayMessage.contains("https://docs.airbyte.com/integrations/sources/mssql"),
            "Expected the connector docs link, got: $displayMessage",
        )
        Assertions.assertFalse(
            displayMessage.lowercase().contains("retry"),
            "The message serves CHECK as well as syncs and must not promise a retry: $displayMessage",
        )
    }

    companion object {
        /**
         * The message of the SQLServerException the driver throws when the socket cannot be opened.
         */
        fun tcpIpConnectionFailed(socketError: String): String =
            "The TCP/IP connection to the host localhost, port 1433 has failed. " +
                "Error: \"$socketError. Verify the connection properties. " +
                "Make sure that an instance of SQL Server is running on the host and accepting " +
                "TCP/IP connections at the port. Make sure that TCP connections to the port are " +
                "not blocked by a firewall.\"."
    }
}
