/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.data.icerberg.parquet.IcebergDestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationCleaner

/**
 * Cleaner for GCS Data Lake (BigLake) integration tests.
 *
 * This cleaner removes old test namespaces and tables from the BigLake catalog to:
 * 1. Reduce quota usage by cleaning up unused resources
 * 2. Prevent test pollution from failed or interrupted tests
 * 3. Keep the test environment clean for subsequent test runs
 */
object GcsDataLakeCleaner : DestinationCleaner {
    private val actualCleaner =
        IcebergDestinationCleaner(
            GcsDataLakeTestUtil.getCatalog(
                GcsDataLakeTestUtil.parseConfig(GcsDataLakeTestUtil.BIGLAKE_CONFIG_PATH)
            )
        )

    override fun cleanup() {
        actualCleaner.cleanup()
    }
}
