/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.fusion

import com.fasterxml.jackson.databind.ObjectMapper
import java.util.UUID
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class FusionContractTest {
    private val id = UUID.fromString("12345678-1234-1234-1234-123456789012")
    private val env =
        mapOf(
            "AIRBYTE_S3_COPY_ENABLED" to "true",
            "AIRBYTE_S3_COPY_ROLE_ARN" to "arn:aws:iam::123456789012:role/fusion",
            "AIRBYTE_S3_COPY_BUCKET" to "archive",
            "AIRBYTE_S3_COPY_REGION" to "us-east-1",
        ) +
            listOf("ORGANIZATION", "WORKSPACE", "SOURCE", "CONNECTION", "DESTINATION").associate {
                "AIRBYTE_${it}_ID" to id.toString()
            }

    @Test
    fun `configured schema retains annotations and extracts nested keys and cursors`() {
        val mapper = ObjectMapper()
        val configured =
            mapper.readTree(
                """{
            "stream": {"json_schema": {"type": "object", "description": "preserved", "properties": {"id": {"type": "string"}}}},
            "primary_key": [["parent", "id"]],
            "cursor_field": ["updated_at"]
        }"""
            )
        val descriptor = FusionSchema.fromConfiguredStream(configured)
        assertEquals(configured["stream"]["json_schema"], descriptor["source_schema"])
        assertEquals(configured["primary_key"], mapper.valueToTree(descriptor["primary_key"]))
        assertEquals(configured["cursor_field"], mapper.valueToTree(descriptor["cursor"]))
        val defaults =
            FusionSchema.fromConfiguredStream(mapper.readTree("""{"stream":{"json_schema":{}}}"""))
        assertEquals(emptyList<Any>(), defaults["primary_key"])
        assertEquals(emptyList<Any>(), defaults["cursor"])
        assertThrows(IllegalArgumentException::class.java) {
            FusionSchema.fromConfiguredStream(mapper.readTree("{}"))
        }
    }

    @Test
    fun `disabled needs no archive configuration`() {
        assertNull(FusionConfiguration.fromEnvironment(emptyMap()))
        assertNull(
            FusionConfiguration.fromEnvironment(env + ("AIRBYTE_S3_COPY_ENABLED" to "false"))
        )
        assertThrows(IllegalArgumentException::class.java) {
            FusionConfiguration.fromEnvironment(env + ("AIRBYTE_S3_COPY_ENABLED" to "yes"))
        }
    }

    @Test
    fun `enabled requires actual platform identity`() {
        assertThrows(IllegalStateException::class.java) {
            FusionConfiguration.fromEnvironment(env - "AIRBYTE_ORGANIZATION_ID")
        }
        assertThrows(IllegalArgumentException::class.java) {
            FusionConfiguration.fromEnvironment(env + ("AIRBYTE_SOURCE_ID" to "1-1-1-1-1"))
        }
    }

    @Test
    fun `injected credentials must be paired and ambient credentials remain available`() {
        val ambient = FusionConfiguration.fromEnvironment(env)!!
        assertNull(ambient.accessKeyId)
        assertNull(ambient.secretAccessKey)
        assertThrows(IllegalArgumentException::class.java) {
            FusionConfiguration.fromEnvironment(env + ("AWS_ASSUME_ROLE_ACCESS_KEY_ID" to "key"))
        }
        val injected =
            FusionConfiguration.fromEnvironment(
                env +
                    mapOf(
                        "AWS_ASSUME_ROLE_ACCESS_KEY_ID" to "key",
                        "AWS_ASSUME_ROLE_SECRET_ACCESS_KEY" to "secret",
                        "AWS_ASSUME_ROLE_EXTERNAL_ID" to "external",
                    )
            )!!
        assertEquals("key", injected.accessKeyId)
        assertEquals("secret", injected.secretAccessKey)
        assertEquals("external", injected.externalId)
        assertFalse(injected.toString().contains("secret"))
    }

    @Test
    fun `run paths preserve platform hierarchy and encode UTF8 key components`() {
        val config = FusionConfiguration.fromEnvironment(env)!!
        assertEquals(
            "fusion/organizations/$id/workspaces/$id/sources/$id/connections/$id/destinations/$id/syncs/streams/a%2Fb%20%C3%A9/runs/42/$id/",
            FusionPaths.run(config, "a/b é", id, 42),
        )
        assertEquals("%2E%2E", FusionPaths.escape(".."))
        assertEquals("a.b", FusionPaths.escape("a.b"))
        assertThrows(IllegalArgumentException::class.java) {
            FusionPaths.run(config, "é".repeat(200), id, 42)
        }
    }

    @Test
    fun `schema identity cannot be overwritten and completion stays minimal`() {
        val metadata = FusionMetadata(FusionConfiguration.fromEnvironment(env)!!, id, 42)
        val descriptor =
            mapOf(
                "source_schema" to mapOf("type" to "object"),
                "primary_key" to listOf(listOf("id")),
                "cursor" to listOf("updated_at"),
                "organization_id" to "incorrect",
                "generation_id" to -1,
            )
        val schema = metadata.schema(descriptor, "hash", 7, 8)
        assertEquals(id, schema["organization_id"])
        assertEquals(7L, schema["generation_id"])
        assertEquals(descriptor["source_schema"], schema["source_schema"])
        assertEquals(descriptor["primary_key"], schema["primary_key"])
        assertEquals(descriptor["cursor"], schema["cursor"])
        assertEquals(mapOf("job_id" to 8L), metadata.streamComplete(8))
        assertEquals(mapOf("job_id" to 8L), metadata.streamComplete(8, 0))
        assertEquals(
            mapOf("job_id" to 8L, "min_generation_id" to 7L),
            metadata.streamComplete(8, 7)
        )
        assertThrows(IllegalArgumentException::class.java) {
            metadata.schema(descriptor - "source_schema", "hash", 7, 8)
        }
        val batch = metadata.batch("stream", 7, 8, "hash", 9, id)
        assertEquals(schema["organization_id"].toString(), batch["organization-id"])
        assertEquals("9", batch["record-count"])
    }
}
