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
                "Authentication Error: Snowflake rejected the key pair (JWT) authentication. " +
                    "Verify that the private key in the connection configuration " +
                    "matches the public key registered on the Snowflake user, and that " +
                    "the username and account are correct.\n" +
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
