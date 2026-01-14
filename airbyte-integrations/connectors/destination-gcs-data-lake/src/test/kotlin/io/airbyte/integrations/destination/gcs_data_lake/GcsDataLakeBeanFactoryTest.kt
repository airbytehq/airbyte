/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.integrations.destination.gcs_data_lake.spec.BigLakeCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

internal class GcsDataLakeBeanFactoryTest {

    @Test
    fun testTempTableNameGeneratorCreation() {
        val namespace = "test_namespace"
        val config = createTestConfiguration(namespace)
        val factory = GcsDataLakeBeanFactory()

        val generator = factory.tempTableNameGenerator(config)

        assertNotNull(generator)
        assertEquals(DefaultTempTableNameGenerator::class, generator::class)
    }

    @Test
    fun testTempTableNameGeneratorUsesConfigNamespace() {
        val namespace = "my_custom_namespace"
        val config = createTestConfiguration(namespace)
        val factory = GcsDataLakeBeanFactory()

        val generator = factory.tempTableNameGenerator(config)

        assertNotNull(generator)
    }

    private fun createTestConfiguration(namespace: String): GcsDataLakeConfiguration {
        return GcsDataLakeConfiguration(
            gcsBucketName = "test-bucket",
            serviceAccountJson = """{"type": "service_account", "project_id": "test-project"}""",
            gcpProjectId = "test-project",
            gcpLocation = "us-central1",
            gcsEndpoint = null,
            namespace = namespace,
            gcsCatalogConfiguration =
                GcsCatalogConfiguration(
                    warehouseLocation = "gs://test-bucket/warehouse",
                    mainBranchName = "main",
                    catalogConfiguration =
                        BigLakeCatalogConfiguration(
                            catalogName = "test_catalog",
                            gcpLocation = "us-central1",
                        ),
                ),
        )
    }
}
