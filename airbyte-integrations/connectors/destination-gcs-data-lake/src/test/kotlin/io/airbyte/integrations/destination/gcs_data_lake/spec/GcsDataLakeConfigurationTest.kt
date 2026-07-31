/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
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
