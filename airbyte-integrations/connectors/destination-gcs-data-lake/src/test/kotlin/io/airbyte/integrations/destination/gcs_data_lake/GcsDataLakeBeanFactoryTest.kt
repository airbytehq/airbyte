/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.TouchedKeys
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.IcebergDeleteFileType
import io.airbyte.integrations.destination.gcs_data_lake.spec.IcebergTableFormatVersion
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

internal class GcsDataLakeBeanFactoryTest {
    private val beanFactory = GcsDataLakeBeanFactory()

    @Test
    fun `automatic delete mode caps aggregate records at touched key limit`() {
        assertThat(
                beanFactory
                    .aggregatePublishingConfig(configuration(IcebergDeleteFileType.AUTOMATIC))
                    .maxRecordsPerAgg,
            )
            .isEqualTo(TouchedKeys.MAX_CURRENT_WRITES.toLong())
    }

    @Test
    fun `positional delete mode caps aggregate records at touched key limit`() {
        assertThat(
                beanFactory
                    .aggregatePublishingConfig(configuration(IcebergDeleteFileType.POSITIONAL))
                    .maxRecordsPerAgg,
            )
            .isEqualTo(TouchedKeys.MAX_CURRENT_WRITES.toLong())
    }

    @Test
    fun `deletion vector mode caps aggregate records at touched key limit`() {
        assertThat(
                beanFactory
                    .aggregatePublishingConfig(
                        configuration(IcebergDeleteFileType.DELETION_VECTOR),
                    )
                    .maxRecordsPerAgg,
            )
            .isEqualTo(TouchedKeys.MAX_CURRENT_WRITES.toLong())
    }

    @Test
    fun `equality delete mode keeps the configured aggregate record limit`() {
        val configuredLimit = TouchedKeys.MAX_CURRENT_WRITES.toLong() + 100L

        assertThat(
                beanFactory
                    .aggregatePublishingConfig(
                        configuration(IcebergDeleteFileType.EQUALITY),
                    )
                    .maxRecordsPerAgg,
            )
            .isEqualTo(configuredLimit)
    }

    private fun configuration(deleteFileType: IcebergDeleteFileType) =
        GcsDataLakeConfiguration(
            gcsBucketName = "bucket",
            serviceAccountJson = "{}",
            gcpProjectId = "project",
            gcpLocation = "us-central1",
            gcsEndpoint = null,
            namespace = "namespace",
            gcsCatalogConfiguration =
                GcsCatalogConfiguration(
                    warehouseLocation = "gs://bucket/",
                    mainBranchName = "main",
                    catalogConfiguration =
                        PolarisCatalogConfiguration(
                            serverUri = "http://localhost:8080/api/catalog",
                            catalogName = "test",
                            clientId = "client",
                            clientSecret = "secret",
                        ),
                ),
            tableFormatVersion =
                if (deleteFileType == IcebergDeleteFileType.DELETION_VECTOR) {
                    IcebergTableFormatVersion.V3
                } else {
                    IcebergTableFormatVersion.V2
                },
            icebergDeleteFileType = deleteFileType,
            maxRecordsPerFlush = TouchedKeys.MAX_CURRENT_WRITES.toLong() + 100L,
        )
}
