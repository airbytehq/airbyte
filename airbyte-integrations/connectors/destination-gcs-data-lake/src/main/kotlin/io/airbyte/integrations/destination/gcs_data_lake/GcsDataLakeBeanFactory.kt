/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.cdk.load.dataflow.config.model.DataFlowSocketConfig
import io.airbyte.cdk.load.dataflow.config.model.MediumConverterConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.MergeOnReadDeleteEncoding
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

@Factory
class GcsDataLakeBeanFactory {
    private val log = KotlinLogging.logger {}

    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig {
        log.info { "NOOP code change for CI to pick up" }

        // NOT speed mode
        return AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000L,
            maxEstBytesPerAgg = 150_000_000L,
            maxEstBytesAllAggregates = 150_000_000L * 5,
            maxBufferedAggregates = 5,
        )
    }

    // TODO: There's a bug preventing the DefaultTempTableNameGenerator Singleton in the CDK
    // from being loaded. So this is necessary for now.
    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    /** Iceberg has specific timestamp requirements */
    @Singleton
    fun mediumConverterConfig() =
        MediumConverterConfig(
            extractedAtAsTimestampWithTimezone = false,
        )

    /** Preserve the production one-socket invariant for all Dedupe streams. */
    @Singleton
    @Requires(notEnv = [Environment.TEST])
    fun dataFlowSocketConfig(catalog: DestinationCatalog): DataFlowSocketConfig {
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
        config: GcsDataLakeConfiguration,
    ): DataFlowSocketConfig {
        val hasPositionalDedupeStreams =
            config.mergeOnReadDeleteEncoding == MergeOnReadDeleteEncoding.POSITIONAL &&
                catalog.streams.any { it.tableSchema.importType is Dedupe }
        return if (hasPositionalDedupeStreams) {
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
