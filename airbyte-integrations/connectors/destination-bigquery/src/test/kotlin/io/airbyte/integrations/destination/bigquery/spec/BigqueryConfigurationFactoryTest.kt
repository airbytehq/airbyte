/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.util.Jsons
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigqueryConfigurationFactoryTest {
    private val factory = BigqueryConfigurationFactory()

    @Test
    fun `parses valid per-stream configuration`() {
        val config =
            factory.makeWithoutExceptionHandling(
                specification(
                    """
                    [
                      {
                        "stream_name": "orders",
                        "stream_namespace": "sales",
                        "destination_dataset": "analytics",
                        "partitioning_field": "created_at",
                        "partitioning_granularity": "MONTH",
                        "clustering_fields": ["customer_id", "status"]
                      }
                    ]
                    """
                )
            )

        val streamConfig = config.streamConfigurations[StreamSelector("sales", "orders")]!!
        assertEquals("analytics", streamConfig.destinationDataset)
        assertEquals(PartitioningGranularity.MONTH, streamConfig.partitioningGranularity)
        assertEquals(listOf("customer_id", "status"), streamConfig.clusteringFields)
    }

    @Test
    fun `rejects duplicate selectors`() {
        assertThrows<ConfigErrorException> {
            factory.makeWithoutExceptionHandling(
                specification(
                    """
                    [
                      {"stream_name": "orders", "stream_namespace": "sales"},
                      {"stream_name": "orders", "stream_namespace": "sales"}
                    ]
                    """
                )
            )
        }
    }

    @Test
    fun `rejects invalid partition and clustering configuration`() {
        assertThrows<ConfigErrorException> {
            factory.makeWithoutExceptionHandling(
                specification(
                    """
                    [
                      {
                        "stream_name": "orders",
                        "partitioning_granularity": "DAY"
                      }
                    ]
                    """
                )
            )
        }

        assertThrows<ConfigErrorException> {
            factory.makeWithoutExceptionHandling(
                specification(
                    """
                    [
                      {
                        "stream_name": "orders",
                        "clustering_fields": ["customer_id", "CUSTOMER_ID"]
                      }
                    ]
                    """
                )
            )
        }
    }

    private fun specification(streamConfigurations: String): BigquerySpecification =
        Jsons.treeToValue(
            Jsons.readTree(
                """
                {
                  "project_id": "project",
                  "dataset_location": "US",
                  "dataset_id": "default_dataset",
                  "stream_configurations": $streamConfigurations
                }
                """
            ),
            BigquerySpecification::class.java,
        )
}
