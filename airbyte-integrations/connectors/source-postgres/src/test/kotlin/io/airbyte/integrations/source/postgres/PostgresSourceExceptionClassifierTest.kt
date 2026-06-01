/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import javax.net.ssl.SSLHandshakeException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
class PostgresSourceExceptionClassifierTest {
    @Inject lateinit var handler: ExceptionHandler

    @Test
    fun `expired TLS certificates are classified as config errors`() {
        val exception =
            RuntimeException(
                "Connection failed",
                SSLHandshakeException(
                    "(certificate_expired) Received fatal alert: certificate_expired",
                ),
            )

        assertEquals(
            ConfigError("Postgres TLS certificate is expired."),
            handler.classify(exception)
        )

        val traceMessage = handler.handle(exception)
        assertEquals(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR, traceMessage.failureType)
        assertEquals("Postgres TLS certificate is expired.", traceMessage.message)
    }
}
