/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class S3CopyConfigurationTest {
    private val enabled =
        mapOf(
            "AIRBYTE_S3_COPY_ENABLED" to "true",
            "AIRBYTE_S3_COPY_BUCKET" to "archive-bucket",
            "AIRBYTE_S3_COPY_REGION" to "us-east-1",
            "AIRBYTE_S3_COPY_ROLE_ARN" to "arn:aws:iam::123456789012:role/archive",
            "AIRBYTE_S3_COPY_WORKSPACE_ID" to "11111111-1111-4111-8111-111111111111",
            "AIRBYTE_S3_COPY_SOURCE_ID" to "22222222-2222-4222-8222-222222222222",
            "AIRBYTE_S3_COPY_CONNECTION_ID" to "33333333-3333-4333-8333-333333333333",
        )

    @Test
    fun `disabled config does not bind enabled-only values`() {
        assertNull(S3CopyConfiguration.fromEnvironment(emptyMap()))
        assertNull(S3CopyConfiguration.fromEnvironment(mapOf("AIRBYTE_S3_COPY_ENABLED" to "false")))
        assertNull(
            S3CopyConfiguration.fromEnvironment(mapOf("AIRBYTE_S3_COPY_WORKSPACE_ID" to "invalid"))
        )
    }

    @Test
    fun `enablement accepts only literal true or false`() {
        listOf("", "TRUE", "False", "1", "yes", " true ").forEach { value ->
            assertThrows(IllegalStateException::class.java) {
                S3CopyConfiguration.fromEnvironment(enabled + ("AIRBYTE_S3_COPY_ENABLED" to value))
            }
        }
    }

    @Test
    fun `enabled requires every authorization and routing value`() {
        enabled.keys
            .filter { it != "AIRBYTE_S3_COPY_ENABLED" }
            .forEach { key ->
                assertThrows(IllegalStateException::class.java) {
                    S3CopyConfiguration.fromEnvironment(enabled - key)
                }
                listOf("", " ", " value ").forEach { value ->
                    assertThrows(IllegalStateException::class.java) {
                        S3CopyConfiguration.fromEnvironment(enabled + (key to value))
                    }
                }
            }
    }

    @Test
    fun `routing rejects shortened uppercase and malformed UUIDs`() {
        listOf("WORKSPACE_ID", "SOURCE_ID", "CONNECTION_ID").forEach { suffix ->
            listOf("1-1-1-1-1", "FFFFFFFF-FFFF-4FFF-8FFF-FFFFFFFFFFFF", "not-a-uuid").forEach {
                value ->
                val exception =
                    assertThrows(IllegalStateException::class.java) {
                        S3CopyConfiguration.fromEnvironment(
                            enabled + ("AIRBYTE_S3_COPY_$suffix" to value)
                        )
                    }
                assertTrue(exception.message!!.contains("canonical"))
            }
        }
    }

    @Test
    fun `prefix defaults normalizes slashes and rejects empty`() {
        val config = S3CopyConfiguration.fromEnvironment(enabled)!!
        assertEquals("fusion", config.prefix)
        assertEquals("archive-bucket", config.bucket)
        assertEquals(enabled["AIRBYTE_S3_COPY_CONNECTION_ID"], config.connectionId.toString())
        assertNull(config.externalId)
        assertEquals(
            "other/nested",
            S3CopyConfiguration.fromEnvironment(
                    enabled + ("AIRBYTE_S3_COPY_PREFIX" to "//other/nested///")
                )!!
                .prefix,
        )
        listOf("", "/", "///", " ").forEach { value ->
            assertThrows(IllegalStateException::class.java) {
                S3CopyConfiguration.fromEnvironment(enabled + ("AIRBYTE_S3_COPY_PREFIX" to value))
            }
        }
    }

    @Test
    fun `external ID is optional but nonblank when supplied`() {
        assertEquals(
            "external",
            S3CopyConfiguration.fromEnvironment(
                    enabled + ("AIRBYTE_S3_COPY_EXTERNAL_ID" to "external")
                )!!
                .externalId,
        )
        assertThrows(IllegalStateException::class.java) {
            S3CopyConfiguration.fromEnvironment(enabled + ("AIRBYTE_S3_COPY_EXTERNAL_ID" to ""))
        }
    }
}
