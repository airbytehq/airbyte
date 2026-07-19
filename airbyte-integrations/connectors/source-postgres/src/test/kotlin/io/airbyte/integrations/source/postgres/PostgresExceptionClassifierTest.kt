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
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["test"])
class PostgresExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testSocketTimeoutConnectTimedOut() {
        val result = classifier.classify(SocketTimeoutException("Connect timed out"))

        assertEquals(
            TransientError(
                "Postgres connection timeout: Database connection timed out, will retry."
            ),
            result,
        )
    }

    @Test
    fun testSocketTimeoutConnectionTimedOut() {
        val result = classifier.classify(SocketTimeoutException("Connection timed out"))

        assertEquals(
            TransientError(
                "Postgres connection timeout: Database connection timed out, will retry."
            ),
            result,
        )
    }

    @Test
    fun testWrappedSocketTimeoutException() {
        val exception =
            RuntimeException(
                "failed to connect",
                SocketTimeoutException("Connect timed out"),
            )

        val result = classifier.classify(exception)

        assertTrue(result is TransientError)
    }

    @Test
    fun testConnectionAttemptFailed() {
        val result =
            classifier.classify(
                RuntimeException(
                    "org.postgresql.util.PSQLException: The connection attempt failed."
                )
            )

        assertEquals(
            TransientError(
                "Postgres connection error: Database connection attempt failed, will retry."
            ),
            result,
        )
    }

    @Test
    fun testNestedConnectionAttemptFailedWithEofCause() {
        val exception =
            RuntimeException(
                "state validation failed",
                RuntimeException(
                    "org.postgresql.util.PSQLException: The connection attempt failed.",
                    java.io.EOFException(),
                ),
            )

        val result = classifier.classify(exception)

        assertEquals(
            TransientError(
                "Postgres connection error: Database connection attempt failed, will retry."
            ),
            result,
        )
    }

    @Test
    fun testExistingHikariConnectionTimeoutRule() {
        val exception =
            RuntimeException(
                "java.sql.SQLTransientConnectionException: HikariPool-x - Connection is not available, request timed out after xms"
            )

        val result = classifier.classify(exception)

        assertEquals(
            TransientError(
                "Postgres Hikari Connection Error: Database read failed due to connection timeout, will retry."
            ),
            result,
        )
    }

    @Test
    fun testExistingMsecTimeoutRule() {
        val result =
            classifier.classify(
                RuntimeException(
                    "java.util.concurrent.TimeoutException: Timed out after 15000 msec"
                )
            )

        assertEquals(
            TransientError("Postgres connection timeout: Database connection timeout, will retry."),
            result,
        )
    }
}
