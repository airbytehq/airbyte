/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import java.util.UUID
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class S3CopyConfigurationTest {
    private val enabled =
        mapOf(
            "AIRBYTE_S3_COPY_ENABLED" to "true",
            "AIRBYTE_S3_COPY_BUCKET" to "archive-bucket",
            "AIRBYTE_S3_COPY_REGION" to "us-east-1",
            "AIRBYTE_S3_COPY_ROLE_ARN" to "arn:aws:iam::123456789012:role/archive",
            "AIRBYTE_ORGANIZATION_ID" to "44444444-4444-4444-8444-444444444444",
            "AIRBYTE_DESTINATION_ID" to "55555555-5555-4555-8555-555555555555",
            "AIRBYTE_WORKSPACE_ID" to "11111111-1111-4111-8111-111111111111",
            "AIRBYTE_SOURCE_ID" to "22222222-2222-4222-8222-222222222222",
            "AIRBYTE_CONNECTION_ID" to "33333333-3333-4333-8333-333333333333",
        )

    @Test
    fun `disabled config does not bind enabled-only values`() {
        assertNull(S3CopyConfiguration.fromEnvironment(emptyMap()))
        assertNull(S3CopyConfiguration.fromEnvironment(mapOf("AIRBYTE_S3_COPY_ENABLED" to "false")))
        assertNull(S3CopyConfiguration.fromEnvironment(mapOf("AIRBYTE_WORKSPACE_ID" to "invalid")))
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
    fun `enabled requires bucket region and role`() {
        listOf("AIRBYTE_S3_COPY_BUCKET", "AIRBYTE_S3_COPY_REGION", "AIRBYTE_S3_COPY_ROLE_ARN")
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
    fun `routing rejects shortened malformed blank and padded UUIDs`() {
        idNames.forEach { suffix ->
            listOf("1-1-1-1-1", "not-a-uuid", "", " ", " 11111111-1111-4111-8111-111111111111 ")
                .forEach { value ->
                    val exception =
                        assertThrows(IllegalStateException::class.java) {
                            S3CopyConfiguration.fromEnvironment(
                                enabled + ("AIRBYTE_$suffix" to value)
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
        assertEquals(enabled["AIRBYTE_CONNECTION_ID"], config.connectionId.toString())
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

    private val idNames =
        listOf("ORGANIZATION_ID", "WORKSPACE_ID", "SOURCE_ID", "CONNECTION_ID", "DESTINATION_ID")

    private fun ids(config: S3CopyConfiguration): List<UUID> =
        listOf(
            config.organizationId,
            config.workspaceId,
            config.sourceId,
            config.connectionId,
            config.destinationId
        )

    @Test
    fun `all routing IDs are optional and independently default to zero`() {
        val withoutIds = enabled - idNames.map { "AIRBYTE_$it" }.toSet()
        assertEquals(List(5) { UUID(0, 0) }, ids(S3CopyConfiguration.fromEnvironment(withoutIds)!!))
        idNames.forEachIndexed { index, name ->
            val actual = ids(S3CopyConfiguration.fromEnvironment(enabled - "AIRBYTE_$name")!!)
            assertEquals(UUID(0, 0), actual[index])
            actual.forEachIndexed { otherIndex, id ->
                if (otherIndex != index)
                    assertEquals(UUID.fromString(enabled["AIRBYTE_${idNames[otherIndex]}"]), id)
            }
        }
    }

    @Test
    fun `legacy copy-specific identity aliases are ignored`() {
        val env =
            (enabled - idNames.map { "AIRBYTE_$it" }.toSet()) +
                idNames.associate { "AIRBYTE_S3_COPY_$it" to UUID(0, 99).toString() }
        assertEquals(List(5) { UUID(0, 0) }, ids(S3CopyConfiguration.fromEnvironment(env)!!))
    }

    @Test
    fun `uppercase canonical UUIDs normalize for every routing ID`() {
        val upper = "ABCDEFAB-CDEF-4ABC-8DEF-ABCDEFABCDEF"
        val env = enabled + idNames.associate { "AIRBYTE_$it" to upper }
        assertEquals(
            List(5) { upper.lowercase() },
            ids(S3CopyConfiguration.fromEnvironment(env)!!).map(UUID::toString)
        )
    }
}
