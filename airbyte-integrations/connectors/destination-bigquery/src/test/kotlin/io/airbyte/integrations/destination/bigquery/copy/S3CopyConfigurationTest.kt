/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
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
            "AIRBYTE_S3_COPY_ORGANIZATION_ID" to "44444444-4444-4444-8444-444444444444",
            "AIRBYTE_S3_COPY_DESTINATION_ID" to "55555555-5555-4555-8555-555555555555",
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

    private val idNames =
        listOf("ORGANIZATION_ID", "WORKSPACE_ID", "SOURCE_ID", "CONNECTION_ID", "DESTINATION_ID")

    private fun runtimeConfig(json: String = "{}"): BigqueryConfiguration =
        BigqueryConfigurationFactory()
            .makeWithoutExceptionHandling(
                Jsons.treeToValue(Jsons.readTree(json), BigquerySpecification::class.java)
            )

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
        val withoutIds = enabled - idNames.map { "AIRBYTE_S3_COPY_$it" }.toSet()
        assertEquals(List(5) { UUID(0, 0) }, ids(S3CopyConfiguration.fromEnvironment(withoutIds)!!))
        idNames.forEachIndexed { index, name ->
            val actual =
                ids(S3CopyConfiguration.fromEnvironment(enabled - "AIRBYTE_S3_COPY_$name")!!)
            assertEquals(UUID(0, 0), actual[index])
            actual.forEachIndexed { otherIndex, id ->
                if (otherIndex != index)
                    assertEquals(
                        UUID.fromString(enabled["AIRBYTE_S3_COPY_${idNames[otherIndex]}"]),
                        id
                    )
            }
        }
    }

    @Test
    fun `uppercase canonical UUIDs normalize for every routing ID`() {
        val upper = "ABCDEFAB-CDEF-4ABC-8DEF-ABCDEFABCDEF"
        val env = enabled + idNames.associate { "AIRBYTE_S3_COPY_$it" to upper }
        assertEquals(
            List(5) { upper.lowercase() },
            ids(S3CopyConfiguration.fromEnvironment(env)!!).map(UUID::toString)
        )
    }

    @Test
    fun `preview forces route and preserves environment credentials and optional IDs`() {
        val env =
            enabled +
                mapOf(
                    "AIRBYTE_S3_COPY_ENABLED" to "false",
                    "AIRBYTE_S3_COPY_PREFIX" to "ignored",
                    "AIRBYTE_S3_COPY_EXTERNAL_ID" to "external",
                    "AWS_SESSION_TOKEN" to "test-session-token",
                )
        val preview = S3CopyConfiguration.previewEnvironment(runtimeConfig(), env)
        assertEquals("test-session-token", preview["AWS_SESSION_TOKEN"])
        assertEquals("false", env["AIRBYTE_S3_COPY_ENABLED"])
        val config = S3CopyConfiguration.fromEnvironment(preview)!!
        assertEquals("airbyte-fusion-context-store", config.bucket)
        assertEquals("us-west-2", config.region)
        assertEquals("arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy", config.roleArn)
        assertEquals("fusion", config.prefix)
        assertEquals("external", config.externalId)
        assertEquals(idNames.map { UUID.fromString(enabled["AIRBYTE_S3_COPY_$it"]) }, ids(config))
        assertNull(
            S3CopyConfiguration.fromEnvironment(preview + ("AIRBYTE_S3_COPY_ENABLED" to "false"))
        )
    }

    @Test
    fun `spec IDs pass through runtime factory and override even invalid environment IDs`() {
        val values = idNames.mapIndexed { index, _ -> "ABCDEFAB-CDEF-4ABC-8DEF-ABCDEFABCDE$index" }
        val json =
            idNames.zip(values).joinToString(",", "{", "}") { (name, value) ->
                "\"${name.lowercase()}\":\"$value\""
            }
        val runtime = runtimeConfig(json)
        assertEquals(
            values,
            listOf(
                runtime.organizationId,
                runtime.workspaceId,
                runtime.sourceId,
                runtime.connectionId,
                runtime.destinationId
            )
        )
        val env = enabled + idNames.associate { "AIRBYTE_S3_COPY_$it" to "invalid" }
        val config =
            S3CopyConfiguration.fromEnvironment(
                S3CopyConfiguration.previewEnvironment(runtime, env)
            )!!
        assertEquals(values.map(UUID::fromString), ids(config))
    }

    @Test
    fun `omitted and explicit null config IDs fall back to environment then zero`() {
        val nullJson = idNames.joinToString(",", "{", "}") { "\"${it.lowercase()}\":null" }
        for (json in listOf("{}", nullJson)) {
            val runtime = runtimeConfig(json)
            assertEquals(
                List<String?>(5) { null },
                listOf(
                    runtime.organizationId,
                    runtime.workspaceId,
                    runtime.sourceId,
                    runtime.connectionId,
                    runtime.destinationId
                )
            )
            val env =
                mapOf("AIRBYTE_S3_COPY_SOURCE_ID" to enabled.getValue("AIRBYTE_S3_COPY_SOURCE_ID"))
            val config =
                S3CopyConfiguration.fromEnvironment(
                    S3CopyConfiguration.previewEnvironment(runtime, env)
                )!!
            assertEquals(
                listOf(
                    UUID(0, 0),
                    UUID(0, 0),
                    UUID.fromString(env.getValue("AIRBYTE_S3_COPY_SOURCE_ID")),
                    UUID(0, 0),
                    UUID(0, 0)
                ),
                ids(config)
            )
        }
    }

    @Test
    fun `invalid supplied config IDs fail instead of falling back to valid environment IDs`() {
        idNames.forEach { name ->
            for (value in listOf("", " ", "1-1-1-1-1", "invalid")) {
                val runtime = runtimeConfig("{\"${name.lowercase()}\":\"$value\"}")
                assertThrows(IllegalStateException::class.java) {
                    S3CopyConfiguration.fromEnvironment(
                        S3CopyConfiguration.previewEnvironment(runtime, enabled)
                    )
                }
            }
        }
    }
}
