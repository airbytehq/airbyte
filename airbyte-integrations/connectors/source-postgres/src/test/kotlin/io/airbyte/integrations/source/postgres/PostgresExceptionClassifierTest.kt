/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.SocketTimeoutException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.postgresql.util.PSQLException
import org.postgresql.util.PSQLState

@MicronautTest
class PostgresExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testSocketTimeoutExceptionClassifiedAsTransient() {
        val exception = SocketTimeoutException("Connect timed out")
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(result is TransientError, "Expected TransientError but got $result")
        assertEquals(
            "Postgres Connection Error: Database connection timed out, will retry.",
            (result as TransientError).displayMessage,
        )
    }

    @Test
    fun testSocketTimeoutWrappedInPSQLExceptionClassifiedAsTransient() {
        val cause = SocketTimeoutException("Connect timed out")
        val exception =
            PSQLException("The connection attempt failed.", PSQLState.CONNECTION_FAILURE, cause)
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(result is TransientError, "Expected TransientError but got $result")
    }

    @Test
    fun testConnectionAttemptFailedClassifiedAsTransient() {
        val exception = RuntimeException("The connection attempt failed.")
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(result is TransientError, "Expected TransientError but got $result")
        assertEquals(
            "Postgres Connection Error: Database connection attempt failed, will retry.",
            (result as TransientError).displayMessage,
        )
    }

    @Test
    fun testNestedSocketTimeoutClassifiedAsTransient() {
        val innerException = SocketTimeoutException("Connect timed out")
        val outerException = RuntimeException("Connection error", innerException)
        val result = classifier.classify(outerException)
        assertNotNull(result)
        assertTrue(result is TransientError, "Expected TransientError but got $result")
    }
}
