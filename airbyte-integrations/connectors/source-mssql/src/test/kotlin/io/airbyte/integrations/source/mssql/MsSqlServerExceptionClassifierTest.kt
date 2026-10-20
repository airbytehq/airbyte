/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ConnectorError
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.ConnectException
import java.net.UnknownHostException
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Exercises the regex rules in `src/main/resources/application.yml`, both directly through the
 * [RegexExceptionClassifier] and through the full [ExceptionHandler] chain.
 *
 * The same rule serves a failed connection test (CHECK) and a failed sync, so the unreachable-host
 * messages must point at the host, port, firewall and the Airbyte Cloud IP allowlist, and must not
 * promise a retry.
 *
 * The regex classifier is configured to run ahead of the CDK's default classifier so that a rule
 * can refine a ConfigErrorException thrown by the CDK itself ("Discovered zero tables."). The
 * chain-level tests pin that ordering and check that typed exceptions no rule matches pass through
 * unchanged.
 */
@MicronautTest
class MsSqlServerExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Inject lateinit var handler: ExceptionHandler

    @Test
    fun testTcpIpConnectionRefusedIsUnreachableHost() {
        // The driver throws a SQLServerException whose message embeds the socket error and whose
        // cause is the java.net exception.
        val exception =
            SQLException(
                tcpIpConnectionFailed("Connection refused"),
                ConnectException("Connection refused"),
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
        // java.net.UnknownHostException is folded into the TCP/IP message by the driver
        // (R_tcpipConnectionFailed), so the TCP/IP rule covers it; there is no separate rule.
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
    fun testTcpIpFailureNestedInChangeEventProducerIsUnreachableHost() {
        // CDC wraps driver failures in the Debezium "change event producer" exception; the
        // unreachable-host rule precedes the change event producer rule, so the nested cause wins.
        val driverException =
            SQLException(
                tcpIpConnectionFailed("Connection refused"),
                ConnectException("Connection refused"),
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

    @Test
    fun testZeroTablesIsConfigErrorWithGrantGuidance() {
        // The CDK's CheckOperation throws this ConfigErrorException; it reaches the regex rule only
        // because the regex classifier is ordered ahead of the default classifier.
        val trace: AirbyteErrorTraceMessage =
            handler.handle(ConfigErrorException("Discovered zero tables."))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        assertZeroTablesGuidance(trace.message)
    }

    @Test
    fun testZeroTablesCheckFailureStatusCarriesGuidance() {
        val (trace: AirbyteErrorTraceMessage, status: AirbyteConnectionStatus) =
            handler.handleCheckFailure(ConfigErrorException("Discovered zero tables."))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertTrue(
            status.message.startsWith(
                ExceptionHandler.COMMON_EXCEPTION_MESSAGE_TEMPLATE.substringBefore("%s"),
            ),
            "Unexpected connection status message: ${status.message}",
        )
        assertZeroTablesGuidance(status.message)
    }

    @Test
    fun testTypedExceptionWithoutMatchingRuleIsUnchanged() {
        // With the regex classifier first, typed exceptions that no rule matches must still be
        // mapped by the default classifier to their raw message.
        val cloudMessage = "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel."
        val cloudTrace: AirbyteErrorTraceMessage =
            handler.handle(ConfigErrorException(cloudMessage))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            cloudTrace.failureType,
        )
        Assertions.assertEquals(cloudMessage, cloudTrace.message)
        // The zero-tables rule is anchored and must leave the CDK's sibling message alone.
        val siblingMessage = "Unable to query any of the 3 discovered table(s)."
        val siblingTrace: AirbyteErrorTraceMessage =
            handler.handle(ConfigErrorException(siblingMessage))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            siblingTrace.failureType,
        )
        Assertions.assertEquals(siblingMessage, siblingTrace.message)
    }

    @Test
    fun testTransientRuleStillWinsThroughTheHandlerChain() {
        val exception =
            SQLException(
                tcpIpConnectionFailed("Connection refused"),
                ConnectException("Connection refused"),
            )
        val trace: AirbyteErrorTraceMessage = handler.handle(exception)
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR,
            trace.failureType,
        )
        Assertions.assertTrue(
            trace.message.contains(
                "Airbyte could not reach SQL Server at the configured host and port",
            ),
            "Unexpected message: ${trace.message}",
        )
    }

    private fun assertZeroTablesGuidance(message: String) {
        Assertions.assertFalse(
            message.contains("Discovered zero tables"),
            "Expected the raw CDK message to be replaced, got: $message",
        )
        Assertions.assertTrue(
            message.contains("No tables are visible to the configured login"),
            "Expected the zero-tables guidance, got: $message",
        )
        Assertions.assertTrue(
            message.contains("db_datareader"),
            "Expected the SELECT grant guidance, got: $message",
        )
        Assertions.assertTrue(
            message.contains("Schemas settings"),
            "Expected the database / schemas guidance, got: $message",
        )
        Assertions.assertTrue(
            message.contains("https://docs.airbyte.com/integrations/sources/mssql#"),
            "Expected a link into the connector docs, got: $message",
        )
    }

    private fun assertUnreachableHost(result: ConnectorError?) {
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val displayMessage = (result as TransientError).displayMessage
        Assertions.assertTrue(
            displayMessage.contains(
                "Airbyte could not reach SQL Server at the configured host and port",
            ),
            "Unexpected message: $displayMessage",
        )
        Assertions.assertTrue(
            displayMessage.contains("Check the host and port"),
            "Unexpected message: $displayMessage",
        )
        Assertions.assertTrue(
            displayMessage.contains(
                "your firewall or security group allows Airbyte's IP addresses",
            ),
            "Expected firewall / Airbyte IP guidance, got: $displayMessage",
        )
        Assertions.assertTrue(
            displayMessage.contains(
                "https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist",
            ),
            "Expected the Airbyte Cloud IP allowlist link, got: $displayMessage",
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
         * The message of the SQLServerException the driver throws when the socket cannot be opened
         * (mssql-jdbc R_tcpipConnectionFailed, with the socket error folded in).
         */
        fun tcpIpConnectionFailed(socketError: String): String =
            "The TCP/IP connection to the host localhost, port 1433 has failed. " +
                "Error: \"$socketError. Verify the connection properties. " +
                "Make sure that an instance of SQL Server is running on the host and accepting " +
                "TCP/IP connections at the port. Make sure that TCP connections to the port are " +
                "not blocked by a firewall.\"."
    }
}
