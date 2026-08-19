/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.stream

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryRegion
import io.airbyte.integrations.destination.bigquery.spec.BigqueryStreamConfiguration
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
import io.airbyte.integrations.destination.bigquery.spec.PartitioningGranularity
import io.airbyte.integrations.destination.bigquery.spec.StreamSelector
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigqueryFinalTableNameGenerator
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigqueryRawTableNameGenerator
import kotlin.test.assertEquals
import kotlin.test.assertNull
import org.junit.jupiter.api.Test

class StreamConfigProviderTest {
    @Test
    fun `namespace-specific configuration takes precedence over name-only configuration`() {
        val nameOnly =
            BigqueryStreamConfiguration(
                streamName = "orders",
                destinationDataset = "shared",
                destinationTable = "orders_all",
            )
        val namespaceSpecific =
            BigqueryStreamConfiguration(
                streamName = "orders",
                streamNamespace = "sales",
                destinationDataset = "sales_analytics",
                destinationTable = "fact_orders",
                tableSuffix = "_v2",
                partitioningField = "created_at",
                partitioningGranularity = PartitioningGranularity.MONTH,
                clusteringFields = listOf("customer_id", "status"),
            )
        val provider = provider(nameOnly, namespaceSpecific)

        val salesOrders = DestinationStream.Descriptor("sales", "orders")
        assertEquals("sales_analytics", provider.getDestinationDataset(salesOrders))
        assertEquals("fact_orders", provider.getDestinationTable(salesOrders))
        assertEquals("_v2", provider.getTableSuffix(salesOrders))
        assertEquals("created_at", provider.getPartitioningField(salesOrders))
        assertEquals(
            PartitioningGranularity.MONTH,
            provider.getPartitioningGranularity(salesOrders),
        )
        assertEquals(
            listOf("customer_id", "status"),
            provider.getClusteringFields(salesOrders),
        )

        val supportOrders = DestinationStream.Descriptor("support", "orders")
        assertEquals("shared", provider.getDestinationDataset(supportOrders))
        assertEquals("orders_all", provider.getDestinationTable(supportOrders))
    }

    @Test
    fun `unconfigured streams preserve connector defaults`() {
        val provider = provider()
        val namespaced = DestinationStream.Descriptor("source_namespace", "events")
        val withoutNamespace = DestinationStream.Descriptor(null, "events")

        assertEquals("source_namespace", provider.getDestinationDataset(namespaced))
        assertEquals("default_dataset", provider.getDestinationDataset(withoutNamespace))
        assertEquals("events", provider.getDestinationTable(namespaced))
        assertEquals("", provider.getTableSuffix(namespaced))
        assertEquals(
            StreamConfigProvider.DEFAULT_PARTITIONING_FIELD,
            provider.getPartitioningField(namespaced),
        )
        assertEquals(
            PartitioningGranularity.DAY,
            provider.getPartitioningGranularity(namespaced),
        )
        assertNull(provider.getClusteringFields(namespaced))
    }

    @Test
    fun `table generators route final tables without changing internal raw table names`() {
        val streamConfiguration =
            BigqueryStreamConfiguration(
                streamName = "orders",
                streamNamespace = "sales",
                destinationDataset = "analytics",
                destinationTable = "fact_orders",
                tableSuffix = "_v2",
            )
        val config = configuration(streamConfiguration)
        val provider = StreamConfigProvider(config)
        val descriptor = DestinationStream.Descriptor("sales", "orders")

        val finalTable = BigqueryFinalTableNameGenerator(config, provider).getTableName(descriptor)
        assertEquals("analytics", finalTable.namespace)
        assertEquals("fact_orders_v2", finalTable.name)

        val rawTable = BigqueryRawTableNameGenerator(config).getTableName(descriptor)
        assertEquals("airbyte_internal", rawTable.namespace)
        assertEquals("sales_raw__stream_orders", rawTable.name)
    }

    private fun provider(
        vararg streamConfigurations: BigqueryStreamConfiguration
    ): StreamConfigProvider = StreamConfigProvider(configuration(*streamConfigurations))

    private fun configuration(
        vararg streamConfigurations: BigqueryStreamConfiguration
    ): BigqueryConfiguration =
        BigqueryConfiguration(
            projectId = "project",
            datasetLocation = BigqueryRegion.US,
            datasetId = "default_dataset",
            loadingMethod = BatchedStandardInsertConfiguration,
            credentialsJson = null,
            cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            internalTableDataset = "airbyte_internal",
            legacyRawTablesOnly = false,
            streamConfigurations =
                streamConfigurations.associateBy {
                    StreamSelector(it.streamNamespace, it.streamName)
                },
        )
}
