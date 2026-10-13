/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ConnectorError
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.postgresql.util.PSQLException
import org.postgresql.util.PSQLState

/**
 * Exercises the regex rules in `src/main/resources/application.yml`, in particular the
 * unreachable-host rules whose output must point the user at the host and port, the Postgres
 * remote-connection settings and the firewall / Airbyte Cloud IP allowlist.
 */
@MicronautTest
class PostgresExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testConnectionAttemptFailedOnUnknownHost() {
        // PgJDBC wraps the UnknownHostException raised by Socket.connect() in this PSQLException.
        val driverException =
            PSQLException(
                "The connection attempt failed.",
                PSQLState.CONNECTION_UNABLE_TO_CONNECT,
                UnknownHostException("nonexistent-host.invalid"),
            )
        val exception = RuntimeException("Failed to open a JDBC connection", driverException)
        assertUnreachableHostConfigError(classifier.classify(exception))
    }

    @Test
    fun testConnectionAttemptFailedOnConnectTimeout() {
        // PgJDBC wraps the SocketTimeoutException raised when connectTimeout elapses the same way.
        val driverException =
            PSQLException(
                "The connection attempt failed.",
                PSQLState.CONNECTION_UNABLE_TO_CONNECT,
                SocketTimeoutException("Connect timed out"),
            )
        val exception = RuntimeException("Failed to open a JDBC connection", driverException)
        assertUnreachableHostConfigError(classifier.classify(exception))
    }

    @Test
    fun testConnectionRefused() {
        val driverException =
            PSQLException(
                "Connection to localhost:5433 refused. Check that the hostname and port are " +
                    "correct and that the postmaster is accepting TCP/IP connections.",
                PSQLState.CONNECTION_UNABLE_TO_CONNECT,
                ConnectException("Connection refused"),
            )
        val exception = RuntimeException("Failed to open a JDBC connection", driverException)
        assertUnreachableHostConfigError(classifier.classify(exception))
    }

    @Test
    fun testConnectionAttemptTimedOut() {
        // Thrown by org.postgresql.Driver when a loginTimeout is set and elapses.
        val driverException =
            PSQLException("Connection attempt timed out.", PSQLState.CONNECTION_UNABLE_TO_CONNECT)
        val exception = RuntimeException("Failed to open a JDBC connection", driverException)
        assertUnreachableHostConfigError(classifier.classify(exception))
    }

    @Test
    fun testUnknownHostExceptionSurfacedDirectly() {
        // RuntimeException(cause) uses cause.toString() as its message, which is how the class
        // name of the UnknownHostException ends up in a message.
        val exception = RuntimeException(UnknownHostException("nonexistent-host.invalid"))
        Assertions.assertEquals(
            "java.net.UnknownHostException: nonexistent-host.invalid",
            exception.message,
        )
        assertUnreachableHostConfigError(classifier.classify(exception))
    }

    @Test
    fun testChangeEventProducerWrappingConnectionFailureStaysTransient() {
        // Mid-sync CDC connection failures are wrapped by Debezium in the change event producer
        // error, whose rule precedes the unreachable-host rules and keeps them retryable.
        val driverException =
            PSQLException("The connection attempt failed.", PSQLState.CONNECTION_UNABLE_TO_CONNECT)
        val exception =
            RuntimeException(
                "An exception occurred in the change event producer. This connector will be stopped.",
                driverException,
            )
        Assertions.assertInstanceOf(TransientError::class.java, classifier.classify(exception))
    }

    @Test
    fun testSyntaxErrorIsNotCaptured() {
        val driverException =
            PSQLException("ERROR: syntax error at or near \"SELEC\"", PSQLState.SYNTAX_ERROR)
        val exception = RuntimeException("Failed to run query", driverException)
        Assertions.assertNull(classifier.classify(exception))
    }

    @Test
    fun testBareConnectionRefusedIsNotCaptured() {
        // Only the PgJDBC sentence is matched, not any message containing "refused".
        val exception = RuntimeException(ConnectException("Connection refused"))
        Assertions.assertNull(classifier.classify(exception))
    }

    private fun assertUnreachableHostConfigError(result: ConnectorError?) {
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        val displayMessage: String = (result as ConfigError).displayMessage
        for (expected in
            listOf(
                "Airbyte could not reach the database at the configured host and port.",
                "Check the host and port, that Postgres accepts remote connections " +
                    "(listen_addresses, pg_hba.conf), and that your firewall or security group " +
                    "allows Airbyte's IP addresses.",
                "https://docs.airbyte.com/platform/operating-airbyte/security#ip-addresses",
                "https://docs.airbyte.com/integrations/sources/postgres",
            )) {
            Assertions.assertTrue(
                displayMessage.contains(expected),
                "Expected '$expected' in: $displayMessage",
            )
        }
    }
}
