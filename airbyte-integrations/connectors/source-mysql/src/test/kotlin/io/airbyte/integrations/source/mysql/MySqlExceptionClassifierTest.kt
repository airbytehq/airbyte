/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.ConnectException
import java.net.UnknownHostException
import java.sql.DriverManager
import java.sql.SQLRecoverableException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class MySqlExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testEofCannotReadResponse() {
        val exception =
            RuntimeException(
                "java.io.EOFException: Can not read response from server. " +
                    "Expected to read 10 bytes, read 5 bytes before connection was unexpectedly lost."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofCannotReadResponseWithThousandsSeparators() {
        val exception =
            RuntimeException(
                "java.sql.SQLException: Error retrieving record: Unexpected Exception: java.io.EOFException message given: " +
                    "Can not read response from server. Expected to read 65,568 bytes, read 40,166 bytes before connection was unexpectedly lost."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofExpectedBytesReceivedOnly() {
        val exception =
            RuntimeException("java.io.EOFException: Expected 252 bytes, received only 227 bytes")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofExpectedBytesReceivedOnlyWithThousandsSeparators() {
        val exception =
            RuntimeException(
                "java.io.EOFException: Expected 65,568 bytes, received only 40,166 bytes"
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofFailedToReadRemaining() {
        val exception =
            RuntimeException(
                "java.io.EOFException: Failed to read remaining 2 of 2 bytes from position 114. " +
                    "Block length: 0. Initial block length: 2."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofFailedToReadNextByte() {
        val exception =
            RuntimeException("java.io.EOFException: Failed to read next byte from position 9093464")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val transient = result as TransientError
        Assertions.assertTrue(
            transient.displayMessage.contains("communication issue"),
            "Expected message about communication issue, got: ${transient.displayMessage}"
        )
    }

    @Test
    fun testChangeEventProducerWithoutKnownCauseStaysConfig() {
        val exception =
            RuntimeException(
                "java.lang.RuntimeException: org.apache.kafka.connect.errors.ConnectException: " +
                    "An exception occurred in the change event producer. This connector will be stopped."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
    }

    @Test
    fun testChangeEventProducerWrappingEofClassifiesAsTransient() {
        // Simulates the real exception chain: ConnectException wrapping an EOFException.
        // The EOF rule precedes the generic change event producer rule, so the nested cause
        // is matched first and the failure is retried instead of surfacing as a config error.
        val eofException = java.io.EOFException("Failed to read next byte from position 9093464")
        val debeziumException = RuntimeException("Failed to deserialize data", eofException)
        val connectException =
            RuntimeException(
                "An exception occurred in the change event producer. This connector will be stopped.",
                debeziumException
            )
        val result = classifier.classify(connectException)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testSchemaErrorStillClassifiedAsConfig() {
        val exception =
            RuntimeException(
                "io.debezium.DebeziumException: Error processing row in banking_safe, " +
                    "internal schema size 11, but row size 1 , restart connector with schema recovery mode."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
    }

    @Test
    fun testTimezoneErrorStillClassifiedAsConfig() {
        val exception =
            RuntimeException(
                "java.sql.SQLException: The server time zone value 'PDT' is unrecognized or represents more than one time zone."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
    }

    @Test
    fun testHikariTimeoutIsTransient() {
        val exception =
            RuntimeException(
                "java.sql.SQLTransientConnectionException: HikariPool-1 - " +
                    "Connection is not available, request timed out after 10 ms"
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    private fun connectionEstablishmentFailure(rootCause: Throwable): Throwable {
        val message =
            "Communications link failure\n\n" +
                "The last packet sent successfully to the server was 0 milliseconds ago. " +
                "The driver has not received any packets from the server."
        return SQLRecoverableException(message, "08S01", 0, RuntimeException(message, rootCause))
    }

    private fun assertConnectionGuidance(result: Any?) {
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val message = (result as TransientError).displayMessage
        Assertions.assertTrue(
            message.startsWith(
                "MySQL Connection Error: MySQL server is unreachable at the configured host and port."
            ),
            "Unexpected message: $message"
        )
        Assertions.assertTrue(
            message.contains("firewall or security group allows inbound connections"),
            message
        )
        Assertions.assertTrue(message.contains("Airbyte's IP addresses"), message)
        Assertions.assertTrue(
            message.contains("\nhttps://docs.airbyte.com/platform/operating-airbyte/ip-allowlist"),
            message
        )
        Assertions.assertTrue(
            message.contains("\nhttps://docs.airbyte.com/integrations/sources/mysql"),
            message
        )
        Assertions.assertFalse(message.contains("will retry"), message)
        Assertions.assertFalse(message.contains("08S01"), message)
        Assertions.assertFalse(message.contains("milliseconds ago"), message)
    }

    @Test
    fun testCommunicationsLinkFailureConnectionRefused() {
        val exception = connectionEstablishmentFailure(ConnectException("Connection refused"))
        assertConnectionGuidance(classifier.classify(exception))
    }

    @Test
    fun testCommunicationsLinkFailureUnknownHost() {
        val exception = connectionEstablishmentFailure(UnknownHostException("no-such-host.invalid"))
        assertConnectionGuidance(classifier.classify(exception))
    }

    @Test
    fun testCommunicationsLinkFailureFromDriverOnClosedPort() {
        val exception =
            Assertions.assertThrows(Throwable::class.java) {
                DriverManager.getConnection(
                    "jdbc:mysql://127.0.0.1:1/db?connectTimeout=5000",
                    "user",
                    "password"
                )
            }
        assertConnectionGuidance(classifier.classify(exception))
    }

    @Test
    fun testMidStreamCommunicationsLinkFailureIsNotTreatedAsUnreachableServer() {
        val message =
            "Communications link failure\n\n" +
                "The last packet successfully received from the server was 1,234 milliseconds ago. " +
                "The last packet sent successfully to the server was 1,235 milliseconds ago."
        Assertions.assertNull(classifier.classify(SQLRecoverableException(message, "08S01", 0)))
        val eof =
            java.io.EOFException(
                "Can not read response from server. Expected to read 4 bytes, " +
                    "read 0 bytes before connection was unexpectedly lost."
            )
        val result = classifier.classify(SQLRecoverableException(message, "08S01", 0, eof))
        Assertions.assertInstanceOf(TransientError::class.java, result)
        Assertions.assertTrue(
            (result as TransientError).displayMessage.startsWith("MySQL EOF Exception:"),
            result.displayMessage
        )
    }

    @Test
    fun testHikariTimeoutWrappingCommunicationsLinkFailureKeepsHikariRule() {
        val exception =
            RuntimeException(
                "java.sql.SQLTransientConnectionException: HikariPool-1 - " +
                    "Connection is not available, request timed out after 10 ms",
                connectionEstablishmentFailure(ConnectException("Connection refused"))
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
        Assertions.assertTrue(
            (result as TransientError).displayMessage.startsWith("Hikari Connection Pool Timeout:"),
            result.displayMessage
        )
    }
}
