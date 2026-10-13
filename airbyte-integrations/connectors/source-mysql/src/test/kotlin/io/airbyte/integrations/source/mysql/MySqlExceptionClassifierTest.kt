/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
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

    @Test
    fun testCommunicationsLinkFailureIsConfigWithReachabilityGuidance() {
        // Connector/J wraps the socket error; the message head is what the rule matches on.
        val exception =
            RuntimeException(
                "com.mysql.cj.jdbc.exceptions.CommunicationsException: Communications link failure\n\n" +
                    "The last packet sent successfully to the server was 0 milliseconds ago. " +
                    "The driver has not received any packets from the server.",
                java.net.ConnectException("Connection refused")
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        assertReachabilityGuidance((result as ConfigError).displayMessage)
    }

    @Test
    fun testUnknownHostExceptionIsConfigWithReachabilityGuidance() {
        val exception = RuntimeException("java.net.UnknownHostException: nonexistent-host.invalid")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        assertReachabilityGuidance((result as ConfigError).displayMessage)
    }

    @Test
    fun testConnectionRefusedIsConfigWithReachabilityGuidance() {
        val exception = RuntimeException("java.net.ConnectException: Connection refused")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        assertReachabilityGuidance((result as ConfigError).displayMessage)
    }

    @Test
    fun testSslRequiredButNotProvidedByServerIsConfigWithTlsOptions() {
        val exception =
            RuntimeException(
                "com.mysql.cj.jdbc.exceptions.CommunicationsException: " +
                    "SSL Connection required, but not provided by server."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        val message: String = (result as ConfigError).displayMessage
        Assertions.assertTrue(message.contains("does not offer TLS"), message)
        Assertions.assertTrue(message.contains("enable TLS on the MySQL server"), message)
        Assertions.assertTrue(message.contains("require_secure_transport"), message)
        Assertions.assertTrue(message.contains("connect through an SSH tunnel"), message)
        Assertions.assertTrue(
            message.contains("preferred SSL mode is not accepted on Airbyte Cloud"),
            message
        )
        Assertions.assertTrue(
            message.contains("https://docs.airbyte.com/integrations/sources/mysql"),
            message
        )
    }

    @Test
    fun testAccessDeniedIsNotCapturedByReachabilityOrTlsRules() {
        val exception =
            RuntimeException(
                "java.sql.SQLException: Access denied for user 'airbyte'@'10.0.0.1' (using password: YES)"
            )
        Assertions.assertNull(classifier.classify(exception))
    }

    private fun assertReachabilityGuidance(message: String) {
        Assertions.assertTrue(
            message.contains("could not reach the database at the configured host and port"),
            message
        )
        Assertions.assertTrue(message.contains("Check the host and port"), message)
        Assertions.assertTrue(message.contains("accepts remote connections"), message)
        Assertions.assertTrue(
            message.contains("firewall or security group allows Airbyte's IP addresses"),
            message
        )
        Assertions.assertTrue(
            message.contains(
                "https://docs.airbyte.com/platform/operating-airbyte/security#ip-addresses"
            ),
            message
        )
        Assertions.assertTrue(
            message.contains("https://docs.airbyte.com/integrations/sources/mysql"),
            message
        )
    }
}
