/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["test"])
class PostgresExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testDatabaseSystemShuttingDown() {
        val exception =
            RuntimeException(
                "org.postgresql.util.PSQLException: FATAL: the database system is shutting down"
            )
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(
            result is TransientError,
            "Expected TransientError but got ${result?.javaClass?.simpleName}: $result",
        )
        val transient = result as TransientError
        assertTrue(
            transient.displayMessage.contains("database system was shutting down"),
            "Unexpected display message: ${transient.displayMessage}",
        )
    }

    @Test
    fun testDatabaseSystemShuttingDownCaseInsensitive() {
        val exception =
            RuntimeException(
                "org.postgresql.util.PSQLException: FATAL: The Database System Is Shutting Down"
            )
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(result is TransientError)
    }

    @Test
    fun testRecoveryInProgressStillClassifiedSeparately() {
        // The recovery-in-progress rule precedes the shutting-down rule and is also
        // classified as transient, but with a different message. Verify it still
        // matches its own rule.
        val exception =
            RuntimeException("org.postgresql.util.PSQLException: ERROR: recovery is in progress")
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(result is TransientError)
        val transient = result as TransientError
        assertTrue(
            transient.displayMessage.contains("recovery mode"),
            "Expected recovery-in-progress message but got: ${transient.displayMessage}",
        )
    }
}
