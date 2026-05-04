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
    fun testTerminatingConnectionDueToAdministratorCommand() {
        val exception =
            RuntimeException(
                "org.postgresql.util.PSQLException: FATAL: terminating connection due to administrator command"
            )
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(
            result is TransientError,
            "Expected TransientError but got ${result?.javaClass?.simpleName}: $result",
        )
        val transient = result as TransientError
        assertTrue(
            transient.displayMessage.contains("The Postgres server terminated the connection"),
            "Unexpected display message: ${transient.displayMessage}",
        )
    }

    @Test
    fun testTerminatingConnectionDueToAdministratorCommandCaseInsensitive() {
        val exception =
            RuntimeException(
                "org.postgresql.util.PSQLException: FATAL: Terminating Connection Due To Administrator Command"
            )
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(result is TransientError)
    }

    @Test
    fun testIdleInTransactionTimeoutStillNotClassifiedAsAdminCommand() {
        // The idle-in-transaction rule precedes the administrator-command rule and is
        // classified as a config error, so it must continue to win for that input.
        val exception =
            RuntimeException(
                "org.postgresql.util.PSQLException: FATAL: terminating connection due to idle-in-transaction timeout"
            )
        val result = classifier.classify(exception)
        assertNotNull(result)
        assertTrue(
            result !is TransientError,
            "idle-in-transaction timeout must not match the administrator-command rule",
        )
    }
}
