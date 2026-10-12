/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.SystemError
import io.airbyte.cdk.output.TransientError
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.io.EOFException
import java.net.ConnectException
import java.net.SocketException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.postgresql.util.PSQLException
import org.postgresql.util.PSQLState

private const val POSTGRES_CONNECTION_ERROR =
    "Airbyte could not reach the Postgres server. Verify the host and port, confirm the server accepts remote connections " +
        "(listen_addresses and pg_hba.conf), and confirm your firewall or security group allows inbound traffic from Airbyte. " +
        "On Airbyte Cloud, allow the Airbyte Cloud IP addresses."
private const val POSTGRES_CONNECTION_REFERENCE =
    "https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist"
private const val EXPECTED =
    "Postgres Connection Error: $POSTGRES_CONNECTION_ERROR\n$POSTGRES_CONNECTION_REFERENCE"
private const val EXISTING_MISSPELLED_RULE =
    "(?i).*an i/o error occured while sending to the backend.*"

@MicronautTest
class PostgresSourceExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Inject lateinit var exceptionHandler: ExceptionHandler

    @Test
    fun testConnectionAttemptFailedWithUnknownHost() {
        val exception =
            postgresException(
                "The connection attempt failed.",
                UnknownHostException("nonexistent-host.invalid")
            )

        Assertions.assertEquals(TransientError(EXPECTED), classifier.classify(exception))
    }

    @Test
    fun testConnectionAttemptFailedWithEofAndSocketTimeoutCauses() {
        listOf(EOFException(), SocketTimeoutException("Connect timed out")).forEach { cause ->
            val exception = postgresException("The connection attempt failed.", cause)

            Assertions.assertEquals(TransientError(EXPECTED), classifier.classify(exception))
        }
    }

    @Test
    fun testConnectionRefused() {
        val exception = refusedConnectionException()

        Assertions.assertEquals(TransientError(EXPECTED), classifier.classify(exception))
    }

    @Test
    fun testWrappedConnectionAttemptFailed() {
        val exception =
            RuntimeException(
                "wrapper",
                postgresException(
                    "The connection attempt failed.",
                    UnknownHostException("nonexistent-host.invalid")
                )
            )

        Assertions.assertEquals(TransientError(EXPECTED), classifier.classify(exception))
    }

    @Test
    fun testConnectionRefusedCheckFailureMessage() {
        val (first, second) = exceptionHandler.handleCheckFailure(refusedConnectionException())

        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            first.failureType
        )
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, second.status)
        Assertions.assertEquals(
            "Could not connect with provided configuration. Error: $EXPECTED",
            second.message
        )
    }

    @Test
    fun testRulesDoNotMatchUnrelatedConnectionErrors() {
        val ioException =
            PSQLException(
                "An I/O error occurred while sending to the backend.",
                PSQLState.CONNECTION_FAILURE,
                SocketException("Connection reset")
            )
        val bareConnectionException = ConnectException("Connection refused")

        listOf(ioException, bareConnectionException).forEach { exception ->
            val result = classifier.classify(exception)
            val message =
                when (result) {
                    is ConfigError -> result.displayMessage
                    is SystemError -> result.displayMessage
                    is TransientError -> result.displayMessage
                    null -> null
                }

            Assertions.assertTrue(
                message == null ||
                    !message.contains("could not reach the Postgres server", ignoreCase = true),
                "Unexpectedly received Postgres connection guidance: $result"
            )
        }
    }

    @Test
    fun testRuleExamplesMatchTheirRegexExceptKnownExistingTypo() {
        val knownMismatch = classifier.rules.single { it.pattern == EXISTING_MISSPELLED_RULE }

        Assertions.assertFalse(knownMismatch.regex.containsMatchIn(knownMismatch.inputExample))
        Assertions.assertTrue(
            classifier.rules
                .filterNot { it == knownMismatch }
                .all { it.regex.containsMatchIn(it.inputExample) },
            "A rule input example did not match its regex"
        )
    }

    private fun refusedConnectionException() =
        postgresException(
            "Connection to localhost:5999 refused. Check that the hostname and port are correct and that the postmaster is accepting TCP/IP connections.",
            ConnectException("Connection refused")
        )

    private fun postgresException(message: String, cause: Throwable) =
        PSQLException(message, PSQLState.CONNECTION_UNABLE_TO_CONNECT, cause)
}
