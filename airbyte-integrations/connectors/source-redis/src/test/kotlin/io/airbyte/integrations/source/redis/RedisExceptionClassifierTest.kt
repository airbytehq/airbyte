/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class RedisExceptionClassifierTest {
    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testModernNopermMessageIsClassified() {
        assertPermissionError(
            "io.lettuce.core.RedisCommandExecutionException: NOPERM User no-scan has no permissions to run the 'scan' command",
        )
    }

    @Test
    fun testLegacyNopermMessageIsClassified() {
        assertPermissionError(
            "io.lettuce.core.RedisCommandExecutionException: NOPERM this user has no permissions to run the 'scan' command or its subcommand",
        )
    }

    @Test
    fun testHostnameMismatchVariantsAreClassified() {
        val messages =
            listOf(
                "javax.net.ssl.SSLHandshakeException: No subject alternative DNS name matching redis.example found",
                "javax.net.ssl.SSLHandshakeException: No subject alternative names present",
                "javax.net.ssl.SSLHandshakeException: No name matching redis.example found",
            )
        val expected =
            ConfigError(
                "Redis server certificate hostname does not match the configured host. Use the hostname listed in the certificate.",
            )

        messages.forEach { message ->
            Assertions.assertEquals(expected, classifier.classify(RuntimeException(message)))
        }
    }

    private fun assertPermissionError(message: String) {
        Assertions.assertEquals(
            ConfigError(
                "Redis does not permit a required command. Grant the configured user permission to run SCAN and DBSIZE.",
            ),
            classifier.classify(RuntimeException(message)),
        )
    }
}
