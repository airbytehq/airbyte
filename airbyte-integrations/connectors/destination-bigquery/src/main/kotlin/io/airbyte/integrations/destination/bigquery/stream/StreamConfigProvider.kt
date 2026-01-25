/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.stream

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.StreamLevelConfig
import jakarta.inject.Singleton

/**
 * Provides stream-level configuration by looking up the config map with fallback to defaults.
 * 
 * Stream lookup order:
 * 1. namespace.stream_name (if namespace is defined)
 * 2. stream_name only
 * 3. Falls back to connector-level defaults
 */
@Singleton
class StreamConfigProvider(
    private val config: BigqueryConfiguration
) {
    /**
     * Get the stream-level configuration for a given stream descriptor.
     * Returns null if no stream-specific config exists.
     */
    fun getStreamConfig(descriptor: DestinationStream.Descriptor): StreamLevelConfig? {
        // Try namespace.stream_name first
        if (descriptor.namespace != null) {
            val fullKey = "${descriptor.namespace}.${descriptor.name}"
            config.streamConfigMap[fullKey]?.let { return it }
        }
        
        // Try stream_name only
        return config.streamConfigMap[descriptor.name]
    }
    
    /**
     * Get the effective clustering field for a stream.
     * Priority: stream config > default config > null (use PK-based)
     */
    fun getClusteringField(descriptor: DestinationStream.Descriptor): String? {
        return getStreamConfig(descriptor)?.clusteringField
            ?: config.defaultClusteringField
    }
    
    /**
     * Get the effective partitioning field for a stream.
     * Priority: stream config > default config > "_airbyte_extracted_at"
     */
    fun getPartitioningField(descriptor: DestinationStream.Descriptor): String {
        return getStreamConfig(descriptor)?.partitioningField
            ?: config.defaultPartitioningField
            ?: "_airbyte_extracted_at"
    }
    
    /**
     * Get the effective table suffix for a stream.
     * Priority: stream config > default config > "" (no suffix)
     */
    fun getTableSuffix(descriptor: DestinationStream.Descriptor): String {
        return getStreamConfig(descriptor)?.tableSuffix
            ?: config.defaultTableSuffix
            ?: ""
    }
    
    /**
     * Get the effective dataset for a stream.
     * Priority: stream config > stream namespace > default dataset
     */
    fun getDataset(descriptor: DestinationStream.Descriptor): String {
        return getStreamConfig(descriptor)?.dataset
            ?: descriptor.namespace
            ?: config.datasetId
    }
}
