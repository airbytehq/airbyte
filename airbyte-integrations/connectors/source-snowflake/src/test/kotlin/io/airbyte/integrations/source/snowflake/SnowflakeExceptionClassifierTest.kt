/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Test

@MicronautTest
class SnowflakeExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Inject lateinit var handler: ExceptionHandler

    @Test
    fun testInvalidJwtKeyPairAuthenticationIsConfigError() {
        val sqlException =
            SQLException(
                "JWT token is invalid. [a1b2c3d4-0000-0000-0000-000000000000]",
                "08001",
                390144
            )
        val exception = RuntimeException("Failed to connect", sqlException)

        assertEquals(
            ConfigError(
                "Authentication Error: " +
                    "Key pair authentication failed. Check that the username is correct and that " +
                    "the private key matches the RSA public key registered on that user (DESCRIBE " +
                    "USER shows RSA_PUBLIC_KEY_FP; ALTER USER ... SET RSA_PUBLIC_KEY registers a " +
                    "new one).\n" +
                    "https://docs.snowflake.com/en/user-guide/key-pair-auth-troubleshooting"
            ),
            classifier.classify(exception)
        )
    }

    @Test
    fun testInvalidJwtKeyPairAuthenticationIsConfigErrorInHandler() {
        val sqlException =
            SQLException(
                "JWT token is invalid. [a1b2c3d4-0000-0000-0000-000000000000]",
                "08001",
                390144
            )
        val exception = RuntimeException("Failed to connect", sqlException)

        assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            handler.handle(exception).failureType
        )
    }

    @Test
    fun testSocketClosedRemainsTransient() {
        assertInstanceOf(
            TransientError::class.java,
            classifier.classify(RuntimeException("Socket is closed"))
        )
    }
}
