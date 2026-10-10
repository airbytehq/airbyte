/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.JdbcExceptionClassifier
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.SystemError
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

/**
 * The exception classifier rules in `application.yml`, with the messages the driver really emits.
 */
@MicronautTest
class SnowflakeExceptionClassifierTest {

    @Inject lateinit var regexClassifier: RegexExceptionClassifier
    @Inject lateinit var jdbcClassifier: JdbcExceptionClassifier

    @Test
    fun invalidJwtIsAConfigError() {
        // What the driver throws for a key pair whose public key is not registered on the user.
        val exception =
            SQLException(
                "JWT token is invalid. [0f811342-c5de-47a0-bd01-f2228f082876]",
                "08001",
                390144
            )
        val result = regexClassifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        val message = (result as ConfigError).displayMessage
        Assertions.assertTrue(message.contains("RSA public key"), message)
        Assertions.assertFalse(message.contains("temporary"), message)
    }

    @Test
    fun closedSocketIsTransient() {
        val result = regexClassifier.classify(RuntimeException("Socket is closed"))
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @ParameterizedTest
    @ValueSource(ints = [390100, 260004])
    fun badCredentialsAreAConfigError(code: Int) {
        val exception = SQLException("Incorrect username or password was specified.", "08001", code)
        val result = jdbcClassifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        Assertions.assertTrue((result as ConfigError).displayMessage.contains("credentials"))
    }

    @Test
    fun missingObjectIsAConfigError() {
        val exception =
            SQLException(
                "SQL compilation error: Database 'NOPE' does not exist or not authorized.",
                "02000",
                2043
            )
        val result = jdbcClassifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
    }

    @Test
    fun unknownSqlErrorIsASystemErrorWithTheCode() {
        val wrapped = RuntimeException("query failed", SQLException("boom", "XX000", 999999))
        val result = jdbcClassifier.classify(wrapped)
        Assertions.assertInstanceOf(SystemError::class.java, result)
        Assertions.assertTrue(
            (result as SystemError).displayMessage!!.contains("Error code: 999999")
        )
    }
}
