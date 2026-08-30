/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.cdk.load.dataflow.config.model.DataFlowSocketConfig
import io.airbyte.cdk.load.dataflow.config.model.LifecycleParallelismConfig
import io.airbyte.cdk.load.dataflow.config.model.MediumConverterConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.integrations.destination.s3_data_lake.spec.MergeOnReadDeleteEncoding
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

@Factory
class S3DataLakeBeanFactory {
    private val log = KotlinLogging.logger {}

    @Singleton
    fun aggregatePublishingConfig(config: S3DataLakeConfiguration): AggregatePublishingConfig {
        val batchSize = config.resolvedFlushBatchSizeBytes
        val maxRecords = config.resolvedMaxRecordsPerFlush
        log.info {
            "Configured flush batch size: $batchSize bytes (${batchSize / 1024 / 1024} MiB), " +
                "max records per flush: $maxRecords"
        }
        return AggregatePublishingConfig(
            maxRecordsPerAgg = maxRecords,
            maxEstBytesPerAgg = batchSize,
            maxEstBytesAllAggregates = 150_000_000L * 5,
            maxBufferedAggregates = 5,
        )
    }

    /** Iceberg has specific timestamp requirements */
    @Singleton
    fun mediumConverterConfig() =
        MediumConverterConfig(
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

    /** Preserve the production one-socket invariant for all Dedupe streams. */
    @Singleton
    @Requires(notEnv = [Environment.TEST])
    fun dataFlowSocketConfig(
        catalog: DestinationCatalog,
    ): DataFlowSocketConfig {
        val hasDedupeStreams = catalog.streams.any { it.tableSchema.importType is Dedupe }
        return if (hasDedupeStreams) {
            log.info { "Dedup streams detected, limiting to 1 socket for data consistency" }
            object : DataFlowSocketConfig {
                override val numSockets: Int = 1
            }
        } else {
            log.info { "No socket restriction required, using all available sockets" }
            object : DataFlowSocketConfig {
                override val numSockets: Int = Int.MAX_VALUE
            }
        }
    }

    /** Positional Dedupe also requires one socket in connector tests. */
    @Singleton
    @Requires(env = [Environment.TEST])
    fun positionalTestDataFlowSocketConfig(
        catalog: DestinationCatalog,
        config: S3DataLakeConfiguration,
    ): DataFlowSocketConfig {
        val positionalEncoding =
            when (config.mergeOnReadDeleteEncoding) {
                // TK-TODO: AUTOMATIC is temporarily wired to positional for prerelease testing;
                // flip it back to equality before release.
                MergeOnReadDeleteEncoding.AUTOMATIC,
                MergeOnReadDeleteEncoding.POSITIONAL -> true
                MergeOnReadDeleteEncoding.EQUALITY -> false
            }
        val hasPositionalDedupStreams =
            positionalEncoding && catalog.streams.any { it.tableSchema.importType is Dedupe }
        return if (hasPositionalDedupStreams) {
            log.info { "Positional dedup streams detected, limiting to 1 test socket" }
            object : DataFlowSocketConfig {
                override val numSockets: Int = 1
            }
        } else {
            object : DataFlowSocketConfig {
                override val numSockets: Int = Int.MAX_VALUE
            }
        }
    }
}
