/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["test"])
class PostgresExceptionClassifierTest {

    @Inject lateinit var regexClassifier: RegexExceptionClassifier

    @Test
    fun testCheckoutTimeoutClassifiedAsTransient() {
        val exception =
            RuntimeException(
                "org.postgresql.util.PSQLException: FATAL: checkout timeout",
            )
        val result = regexClassifier.classify(exception)
        Assertions.assertNotNull(result)
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val transientError = result as TransientError
        Assertions.assertTrue(
            transientError.displayMessage.contains("Connection pool checkout timed out"),
            "Expected display message to contain 'Connection pool checkout timed out' but was: ${transientError.displayMessage}",
        )
    }

    @Test
    fun testCheckoutTimeoutWrappedInSQLException() {
        val cause = SQLException("FATAL: checkout timeout", "58000", 0)
        val exception = RuntimeException("query failed", cause)
        val result = regexClassifier.classify(exception)
        Assertions.assertNotNull(result)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testCheckoutTimeoutCaseInsensitive() {
        val exception = RuntimeException("FATAL: CHECKOUT TIMEOUT")
        val result = regexClassifier.classify(exception)
        Assertions.assertNotNull(result)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testUnrelatedExceptionNotMatchedByCheckoutTimeout() {
        val exception = RuntimeException("some other database error")
        val result = regexClassifier.classify(exception)
        Assertions.assertNull(result)
    }
}
