/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.stream

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryStreamConfiguration
import io.airbyte.integrations.destination.bigquery.spec.PartitioningGranularity
import io.airbyte.integrations.destination.bigquery.spec.StreamSelector
import jakarta.inject.Singleton

@Singleton
class StreamConfigProvider(private val config: BigqueryConfiguration) {
    /**
     * Namespace-specific entries take precedence over name-only entries. Descriptors are the mapped
     * destination descriptors supplied by the CDK, so a namespace selector refers to the effective
     * destination namespace.
     */
    fun getStreamConfig(
        descriptor: DestinationStream.Descriptor,
    ): BigqueryStreamConfiguration? =
        config.streamConfigurations[StreamSelector(descriptor.namespace, descriptor.name)]
            ?: config.streamConfigurations[StreamSelector(null, descriptor.name)]

    fun getDestinationDataset(descriptor: DestinationStream.Descriptor): String =
        getStreamConfig(descriptor)?.destinationDataset ?: descriptor.namespace ?: config.datasetId

    fun getDestinationTable(descriptor: DestinationStream.Descriptor): String =
        getStreamConfig(descriptor)?.destinationTable ?: descriptor.name

    fun getTableSuffix(descriptor: DestinationStream.Descriptor): String =
        getStreamConfig(descriptor)?.tableSuffix ?: ""

    fun getPartitioningField(descriptor: DestinationStream.Descriptor): String =
        getStreamConfig(descriptor)?.partitioningField ?: DEFAULT_PARTITIONING_FIELD

    fun getPartitioningGranularity(
        descriptor: DestinationStream.Descriptor,
    ): PartitioningGranularity =
        getStreamConfig(descriptor)?.partitioningGranularity ?: PartitioningGranularity.DAY

    fun getClusteringFields(descriptor: DestinationStream.Descriptor): List<String>? =
        getStreamConfig(descriptor)?.clusteringFields

    companion object {
        const val DEFAULT_PARTITIONING_FIELD = "_airbyte_extracted_at"
    }
}
