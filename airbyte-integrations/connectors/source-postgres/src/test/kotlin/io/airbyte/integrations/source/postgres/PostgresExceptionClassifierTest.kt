/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

@MicronautTest
class PostgresExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testInputExamplesMatchPatterns() {
        // Verify all rules' input-examples actually match their regex patterns.
        for (rule in classifier.rules) {
            val result = rule.matches(RuntimeException(rule.inputExample))
            Assertions.assertTrue(result) {
                "Rule pattern '${rule.pattern}' does not match its own " +
                    "input-example: '${rule.inputExample}'"
            }
        }
    }

    @Test
    fun testIoErrorOccurredClassifiedAsTransient() {
        val message =
            "org.postgresql.util.PSQLException: An I/O error occurred while sending to the backend."
        val result = classifier.classify(RuntimeException(message))
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofExceptionClassifiedAsTransient() {
        val message = "java.io.EOFException"
        val result = classifier.classify(RuntimeException(message))
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofExceptionNestedInPsqlExceptionClassifiedAsTransient() {
        val eofException = RuntimeException("java.io.EOFException")
        val psqlException =
            RuntimeException(
                "org.postgresql.util.PSQLException: An I/O error occurred while sending to the backend.",
                eofException,
            )
        val result = classifier.classify(psqlException)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "org.postgresql.util.PSQLException: An I/O error occurred while sending to the backend.",
                "java.io.EOFException",
                "java.io.EOFException: null",
                "org.postgresql.util.PSQLException: This connection has been closed.",
                "java.net.SocketException: Broken pipe",
                "java.net.SocketException: Socket is closed",
                "HikariPool-1 - Connection is not available, request timed out after 30000ms",
            ],
    )
    fun testTransientConnectionErrors(message: String) {
        val result = classifier.classify(RuntimeException(message))
        Assertions.assertInstanceOf(TransientError::class.java, result) {
            "Expected transient error classification for message: '$message'"
        }
    }
}
