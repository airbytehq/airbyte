/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.SystemErrorException
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class S3CopyConfigurationTest {
    @Test
    fun `enabled writes report missing shared routing IDs as system errors`() {
        val error =
            assertThrows(SystemErrorException::class.java) {
                BigqueryS3CopyFactory.createForOperation(
                    "write",
                    mapOf(
                        "AIRBYTE_S3_COPY_ENABLED" to "true",
                        "AIRBYTE_S3_COPY_BUCKET" to "archive",
                        "AIRBYTE_S3_COPY_REGION" to "us-east-1",
                        "AIRBYTE_S3_COPY_ROLE_ARN" to "arn:aws:iam::123456789012:role/archive",
                    )
                ) { error("Missing routing must fail before construction") }
            }
        assertTrue(error.message!!.contains("AIRBYTE_CONNECTION_ID"))
    }

    @Test
    fun `malformed shared enablement becomes a system error`() {
        assertThrows(SystemErrorException::class.java) {
            BigqueryS3CopyFactory.createForOperation(
                "write",
                mapOf("AIRBYTE_S3_COPY_ENABLED" to "TRUE")
            ) { error("Malformed config must fail before construction") }
        }
    }
}
