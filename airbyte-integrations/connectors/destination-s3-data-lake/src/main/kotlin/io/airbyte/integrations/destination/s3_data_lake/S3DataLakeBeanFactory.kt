/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.cdk.load.dataflow.config.model.DataFlowSocketConfig
import io.airbyte.cdk.load.dataflow.config.model.JsonConverterConfig
import io.airbyte.cdk.load.dataflow.config.model.LifecycleParallelismConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

@Factory
class S3DataLakeBeanFactory {
    private val log = KotlinLogging.logger {}

    @Singleton
    fun aggregatePublishingConfig() =
        AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000L,
            maxEstBytesPerAgg =
                200L * 1024L * 1024L, // copied from DEFAULT_RECORD_BATCH_SIZE_BYTES in legacy-cdk
            maxEstBytesAllAggregates = 150_000_000L * 5,
            maxBufferedAggregates = 5,
        )

    /** Iceberg has specific timestamp requirements */
    @Singleton
    fun jsonConvertConfig() =
        JsonConverterConfig(
            extractedAtAsTimestampWithTimezone = false,
        )

    /**
     * Glue does not tolerate any concurrent modifications when creating tables (aka 'stream init').
     */
    @Singleton
    fun defaultLifecycleParallelismConfig() =
        LifecycleParallelismConfig(
            streamInitParallelism = 1,
        )

    // TODO: There's a bug preventing the DefaultTempTableNameGenerator Singleton in the CDK
    // from being loaded. So this is necessary for now.
    @Singleton fun tempTableNameGenerator() = DefaultTempTableNameGenerator()

    /**
     * Socket configuration for S3 Data Lake destination.
     * - In test environments: this bean is not created, so all sockets are used
     * - In production with dedup streams: limits to 1 socket for data consistency
     * - In production without dedup streams: uses all available sockets
     */
    @Singleton
    @Requires(notEnv = [Environment.TEST])
    fun dataFlowSocketConfig(catalog: DestinationCatalog): DataFlowSocketConfig {
        val hasDedupStreams = catalog.streams.any { it.importType is Dedupe }
        return if (hasDedupStreams) {
            log.info { "Dedup streams detected, limiting to 1 socket for data consistency" }
            object : DataFlowSocketConfig {
                override val numSockets: Int = 1
            }
        } else {
            log.info { "No dedup streams detected, using all available sockets" }
            object : DataFlowSocketConfig {
                override val numSockets: Int = Int.MAX_VALUE
            }
        }
    }
}
