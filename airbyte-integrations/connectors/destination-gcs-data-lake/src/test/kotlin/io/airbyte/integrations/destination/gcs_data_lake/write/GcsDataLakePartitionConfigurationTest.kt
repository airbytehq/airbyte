/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsPartitionFieldSpec
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsPartitionTransform
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.Test

class GcsDataLakePartitionConfigurationTest {
    private fun configuration(fields: List<GcsPartitionFieldSpec>) =
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
            partitionFields = fields,
        )

    @Test
    fun `bucket requires a positive argument`() {
        val error =
            assertFailsWith<ConfigErrorException> {
                configuration(
                    listOf(
                        GcsPartitionFieldSpec("id", GcsPartitionTransform.BUCKET),
                    ),
                )
            }

        kotlin.test.assertContains(error.message.orEmpty(), "transform_argument is required")
    }

    @Test
    fun `truncate rejects a zero argument`() {
        val error =
            assertFailsWith<ConfigErrorException> {
                configuration(
                    listOf(
                        GcsPartitionFieldSpec(
                            "name",
                            GcsPartitionTransform.TRUNCATE,
                            transformArgument = 0,
                        ),
                    ),
                )
            }

        kotlin.test.assertContains(error.message.orEmpty(), "must be at least 1")
    }

    @Test
    fun `other transforms reject an argument`() {
        val error =
            assertFailsWith<ConfigErrorException> {
                configuration(
                    listOf(
                        GcsPartitionFieldSpec(
                            "id",
                            GcsPartitionTransform.IDENTITY,
                            transformArgument = 2,
                        ),
                    ),
                )
            }

        kotlin.test.assertContains(
            error.message.orEmpty(),
            "only supported for BUCKET and TRUNCATE",
        )
    }

    @Test
    fun `blank source column is rejected`() {
        val error =
            assertFailsWith<ConfigErrorException> {
                configuration(
                    listOf(
                        GcsPartitionFieldSpec(" ", GcsPartitionTransform.IDENTITY),
                    ),
                )
            }

        kotlin.test.assertContains(error.message.orEmpty(), "column must not be blank")
    }

    @Test
    fun `valid bucket and truncate arguments are accepted`() {
        configuration(
            listOf(
                GcsPartitionFieldSpec("id", GcsPartitionTransform.BUCKET, transformArgument = 4),
                GcsPartitionFieldSpec(
                    "name",
                    GcsPartitionTransform.TRUNCATE,
                    transformArgument = 2,
                ),
            ),
        )
    }
}
