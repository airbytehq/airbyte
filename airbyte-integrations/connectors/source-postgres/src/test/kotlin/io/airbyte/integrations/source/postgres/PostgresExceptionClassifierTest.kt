/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

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
 *
 * The [ExceptionHandler] tests cover the whole classifier chain: the connector orders the regex
 * classifier ahead of the default one so that a rule can refine a [ConfigErrorException] the CDK
 * throws, such as "Discovered zero tables.", while typed exceptions that match no rule keep their
 * message.
 */
@MicronautTest
class PostgresExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Inject lateinit var handler: ExceptionHandler

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

    @Test
    fun testRegexClassifierRunsAheadOfDefaultClassifier() {
        // application.yml sets airbyte.connector.exception-classifiers.regex.order to 0, ahead of
        // the DefaultExceptionClassifier (1) and the JdbcExceptionClassifier (100).
        Assertions.assertInstanceOf(
            RegexExceptionClassifier::class.java,
            handler.classifiers.first(),
        )
    }

    @Test
    fun testDiscoveredZeroTablesIsRefinedWithPostgresGuidance() {
        // Thrown by the CDK's CheckOperation when no table is found in any discovered schema.
        val trace: AirbyteErrorTraceMessage =
            handler.handle(ConfigErrorException("Discovered zero tables."))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        Assertions.assertTrue(
            trace.message.startsWith(ZERO_TABLES_GUIDANCE),
            "Expected the zero-tables guidance in: ${trace.message}",
        )
        Assertions.assertTrue(
            trace.message.contains(
                "https://docs.airbyte.com/integrations/sources/postgres" +
                    "#step-1-create-a-dedicated-read-only-postgres-user",
            ),
            "Expected the read-only user docs link in: ${trace.message}",
        )
    }

    @Test
    fun testTypedConfigErrorWithoutMatchingRuleKeepsItsMessage() {
        // Thrown by PostgresSourceMetadataQuerier on Airbyte Cloud; no regex rule matches it, so
        // the DefaultExceptionClassifier still maps it to its raw message.
        val message =
            "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel. " +
                "Current SSL mode: disable"
        val trace: AirbyteErrorTraceMessage = handler.handle(ConfigErrorException(message))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        Assertions.assertEquals(message, trace.message)
    }

    @Test
    fun testTransientRuleStillYieldsTransientErrorThroughHandler() {
        val driverException =
            PSQLException("The connection attempt failed.", PSQLState.CONNECTION_UNABLE_TO_CONNECT)
        val exception =
            RuntimeException(
                "An exception occurred in the change event producer. This connector will be stopped.",
                driverException,
            )
        val trace: AirbyteErrorTraceMessage = handler.handle(exception)
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR,
            trace.failureType,
        )
    }

    @Test
    fun testCheckFailureOnDiscoveredZeroTables() {
        val (trace: AirbyteErrorTraceMessage, status: AirbyteConnectionStatus) =
            handler.handleCheckFailure(ConfigErrorException("Discovered zero tables."))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertTrue(
            status.message.startsWith(
                "Could not connect with provided configuration. Error: $ZERO_TABLES_GUIDANCE",
            ),
            "Unexpected connection status message: ${status.message}",
        )
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
                "https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist",
                "https://docs.airbyte.com/integrations/sources/postgres",
            )) {
            Assertions.assertTrue(
                displayMessage.contains(expected),
                "Expected '$expected' in: $displayMessage",
            )
        }
    }

    companion object {
        const val ZERO_TABLES_GUIDANCE: String =
            "No tables are visible to the configured user in the selected database and schemas. " +
                "Grant USAGE on each schema and SELECT on the tables to sync " +
                "(GRANT USAGE ON SCHEMA <schema> TO <user>; " +
                "GRANT SELECT ON ALL TABLES IN SCHEMA <schema> TO <user>), " +
                "check the database name and the Schemas setting, " +
                "and check that no table filter excludes every table."
    }
}
