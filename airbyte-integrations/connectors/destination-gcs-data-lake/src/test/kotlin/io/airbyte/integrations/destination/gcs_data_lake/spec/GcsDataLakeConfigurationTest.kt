/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class GcsDataLakeConfigurationTest {

    @Test
    fun `variant types require format version 3`() {
        assertThrows<ConfigErrorException> {
            configuration(IcebergTableFormatVersion.V2, useVariantTypes = true)
        }
    }

    @Test
    fun `variant types are allowed at format version 3`() {
        assertDoesNotThrow { configuration(IcebergTableFormatVersion.V3, useVariantTypes = true) }
    }

    @Test
    fun `format version 2 without variant types is valid`() {
        assertDoesNotThrow { configuration(IcebergTableFormatVersion.V2, useVariantTypes = false) }
    }

    @Test
    fun `the spec value of the format version deserializes`() {
        val spec =
            ObjectMapper()
                .readValue(
                    """{"table_format_version": "v3", "use_variant_types": true}""",
                    GcsDataLakeSpecification::class.java,
                )

        assertEquals(IcebergTableFormatVersion.V3, spec.tableFormatVersion)
        assertEquals(true, spec.useVariantTypes)
    }

    @Test
    fun `a config without the new fields keeps the previous behavior`() {
        val spec = ObjectMapper().readValue("{}", GcsDataLakeSpecification::class.java)

        assertNull(spec.tableFormatVersion)
        assertNull(spec.useVariantTypes)
    }

    private fun configuration(
        tableFormatVersion: IcebergTableFormatVersion,
        useVariantTypes: Boolean,
    ) =
        GcsDataLakeConfiguration(
            gcsBucketName = "bucket",
            serviceAccountJson = "{}",
            gcpProjectId = "project",
            gcpLocation = "us-central1",
            gcsEndpoint = null,
            namespace = "namespace",
            gcsCatalogConfiguration =
                GcsCatalogConfiguration(
                    warehouseLocation = "gs://bucket/warehouse",
                    mainBranchName = "main",
                    catalogConfiguration = BigLakeCatalogConfiguration("catalog", "project"),
                ),
            tableFormatVersion = tableFormatVersion,
            useVariantTypes = useVariantTypes,
        )
}
