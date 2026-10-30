/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.command.ValidatedJsonUtils
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class GcsV2SpecificationTest {
    private fun parse(pathFields: String): GcsV2Specification =
        ValidatedJsonUtils.parseUnvalidated(
            """
            {
              "gcs_bucket_name": "bucket",
              "gcs_bucket_path": "landing",
              "credential": {
                "credential_type": "HMAC_KEY",
                "hmac_key_access_id": "id",
                "hmac_key_secret": "secret"
              },
              "format": {"format_type": "JSONL"}
              $pathFields
            }
            """
                .trimIndent(),
            GcsV2Specification::class.java,
        )

    @Test
    fun `omitted path fields use defaults`() {
        val config = parse("").toObjectStoragePathConfiguration()
        assertEquals(GcsV2Specification.DEFAULT_PATH_FORMAT, config.pathPattern)
        assertEquals(GcsV2Specification.DEFAULT_FILE_FORMAT, config.fileNamePattern)
    }

    @Test
    fun `blank path fields use defaults`() {
        val config =
            parse(""", "gcs_path_format": "", "file_name_pattern": "  " """)
                .toObjectStoragePathConfiguration()
        assertEquals(GcsV2Specification.DEFAULT_PATH_FORMAT, config.pathPattern)
        assertEquals(GcsV2Specification.DEFAULT_FILE_FORMAT, config.fileNamePattern)
    }

    @Test
    fun `custom path fields are preserved`() {
        val config =
            parse(
                    """, "gcs_path_format": "${'$'}{STREAM_NAME}/dt=${'$'}{YEAR}-${'$'}{MONTH}-${'$'}{DAY}/", "file_name_pattern": "{date}_{part_number}{format_extension}" """,
                )
                .toObjectStoragePathConfiguration()
        assertEquals("\${STREAM_NAME}/dt=\${YEAR}-\${MONTH}-\${DAY}/", config.pathPattern)
        assertEquals("{date}_{part_number}{format_extension}", config.fileNamePattern)
    }
}
