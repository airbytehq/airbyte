/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.integrations.destination.bigquery.copy.BigqueryS3Copy
import io.airbyte.integrations.destination.bigquery.copy.DisabledBigqueryS3Copy
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.stagesAvroFiles
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class BigqueryConfigurationTest {
    @ParameterizedTest
    @CsvSource(
        "'GCS Staging', '', false, false",
        "'GCS Staging', '\"staging_file_format\": \"CSV (gzip)\",', false, false",
        "'GCS Staging', '\"staging_file_format\": \"Avro\",', false, true",
        "'GCS Staging', '\"staging_file_format\": \"Avro\",', true, false",
        "'Storage Write API', '\"staging_file_format\": \"Avro\",', false, false",
    )
    fun `Avro is staged only when GCS staging selects it outside legacy raw tables mode`(
        method: String,
        fileFormat: String,
        legacyRawTables: Boolean,
        expected: Boolean,
    ) {
        val spec =
            ValidatedJsonUtils.parseOne(
                BigquerySpecification::class.java,
                """
                {
                  "project_id": "p",
                  "dataset_location": "US",
                  "dataset_id": "d",
                  "disable_type_dedupe": $legacyRawTables,
                  "loading_method": {
                    "method": "$method",
                    $fileFormat
                    "gcs_bucket_name": "b",
                    "gcs_bucket_path": "p",
                    "credential": {
                      "credential_type": "HMAC_KEY",
                      "hmac_key_access_id": "id",
                      "hmac_key_secret": "secret"
                    }
                  }
                }
                """,
            )
        val config = BigqueryConfigurationFactory().makeWithoutExceptionHandling(spec)

        assertEquals(expected, config.stagesAvroFiles)
    }

    @Test
    fun `Avro is not staged while the Fusion archive is enabled`() {
        val spec =
            ValidatedJsonUtils.parseOne(
                BigquerySpecification::class.java,
                """
                {
                  "project_id": "p",
                  "dataset_location": "US",
                  "dataset_id": "d",
                  "loading_method": {
                    "method": "GCS Staging",
                    "staging_file_format": "Avro",
                    "gcs_bucket_name": "b",
                    "gcs_bucket_path": "p",
                    "credential": {
                      "credential_type": "HMAC_KEY",
                      "hmac_key_access_id": "id",
                      "hmac_key_secret": "secret"
                    }
                  }
                }
                """,
            )
        val config = BigqueryConfigurationFactory().makeWithoutExceptionHandling(spec)

        assertTrue(config.stagesAvroFiles(DisabledBigqueryS3Copy))
        assertFalse(config.stagesAvroFiles(mockk<BigqueryS3Copy>()))
    }
}
