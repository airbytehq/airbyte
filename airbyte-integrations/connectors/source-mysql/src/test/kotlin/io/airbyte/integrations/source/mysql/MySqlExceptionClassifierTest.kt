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
            RuntimeException(
                "java.io.EOFException: Failed to read next byte from position 9093464"
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val transient = result as TransientError
        Assertions.assertTrue(
            transient.displayMessage.contains("communication issue"),
            "Expected message about communication issue, got: ${transient.displayMessage}"
        )
    }

    @Test
    fun testChangeEventProducerIsTransient() {
        val exception =
            RuntimeException(
                "java.lang.RuntimeException: org.apache.kafka.connect.errors.ConnectException: " +
                    "An exception occurred in the change event producer. This connector will be stopped."
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val transient = result as TransientError
        Assertions.assertTrue(
            transient.displayMessage.contains("will retry"),
            "Expected message about retry, got: ${transient.displayMessage}"
        )
    }

    @Test
    fun testChangeEventProducerWrappingEofClassifiesAsTransient() {
        // Simulates the real exception chain: ConnectException wrapping an EOFException
        val eofException =
            java.io.EOFException("Failed to read next byte from position 9093464")
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
}
