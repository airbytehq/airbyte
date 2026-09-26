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
            "AIRBYTE_FUSION_ENABLED" to "true",
            "AIRBYTE_FUSION_S3_BUCKET" to "archive-bucket",
            "AIRBYTE_FUSION_S3_REGION" to "us-east-1",
            "AIRBYTE_FUSION_S3_ROLE_ARN" to "arn:aws:iam::123456789012:role/archive",
            "AIRBYTE_ORGANIZATION_ID" to "44444444-4444-4444-8444-444444444444",
            "AIRBYTE_DESTINATION_ID" to "55555555-5555-4555-8555-555555555555",
            "AIRBYTE_WORKSPACE_ID" to "11111111-1111-4111-8111-111111111111",
            "AIRBYTE_SOURCE_ID" to "22222222-2222-4222-8222-222222222222",
            "AIRBYTE_CONNECTION_ID" to "33333333-3333-4333-8333-333333333333",
        )

    @Test
    fun `disabled config does not bind enabled-only values`() {
        assertNull(S3CopyConfiguration.fromEnvironment(emptyMap()))
        assertNull(S3CopyConfiguration.fromEnvironment(mapOf("AIRBYTE_FUSION_ENABLED" to "false")))
        assertNull(S3CopyConfiguration.fromEnvironment(mapOf("AIRBYTE_WORKSPACE_ID" to "invalid")))
    }

    @Test
    fun `platform routing and assume role credentials use shared configuration`() {
        val config =
            S3CopyConfiguration.fromEnvironment(
                enabled +
                    mapOf(
                        "AWS_ASSUME_ROLE_EXTERNAL_ID" to "external",
                        "AWS_ASSUME_ROLE_ACCESS_KEY_ID" to "bootstrap-access",
                        "AWS_ASSUME_ROLE_SECRET_ACCESS_KEY" to "bootstrap-secret",
                    )
            )!!
        assertEquals("archive-bucket", config.bucket)
        assertEquals("us-east-1", config.region)
        assertEquals("fusion", config.prefix)
        assertEquals("external", config.externalId)
        assertEquals("bootstrap-access", config.accessKeyId)
        assertEquals("bootstrap-secret", config.secretAccessKey)
        assertEquals(idNames.map { UUID.fromString(enabled["AIRBYTE_$it"]) }, ids(config))
    }

    @Test
    fun `enabled write rejects missing platform identity before creating archive`() {
        idNames.forEach { name ->
            assertThrows(io.airbyte.cdk.SystemErrorException::class.java) {
                BigqueryS3CopyFactory.createForOperation("write", enabled - "AIRBYTE_$name") {
                    error("Archive must not be constructed for invalid platform configuration")
                }
            }
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
            config.destinationId,
        )
}
