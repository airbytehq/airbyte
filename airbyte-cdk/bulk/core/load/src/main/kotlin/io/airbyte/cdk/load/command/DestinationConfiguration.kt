/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.command.Configuration
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.nio.file.Path

/**
 * To implement a [DestinationConfiguration]:
 *
 * - Create a class `{MyDestination}Specification` extending [ConfigurationSpecification]
 *
 * - Add any mixin `...Specification`s from this package (the jackson annotations will be inherited)
 *
 * - Add any required custom fields to the spec w/ jackson annotations
 *
 * - Add annotation overrides (note that this will replace the original annotation, so to extend an
 * existing annotation, you must copy the original annotation and add the new fields).
 *
 * - Create a class `{MyDestination}Configuration` extending [DestinationConfiguration]
 *
 * - Add the corresponding mixin `...ConfigurationProvider`s for any added spec mixins
 *
 * - (Add overrides for any fields provided by the providers)
 *
 * - Add custom config to the configuration as needed
 *
 * - Implement `DestinationConfigurationFactory` as a @[Singleton], using the `to...Configuration`
 * methods from the specs to map to the provided configuration fields
 *
 * - (Set your custom fields as needed.)
 *
 * - Add a @[Factory] injected with [DestinationConfiguration], returning a @[Singleton] downcast to
 * your implementation; ie,
 *
 * ```
 *   @Factory
 *   class MyDestinationConfigurationProvider(
 *      private val config: DestinationConfiguration
 *   ){
 *    @Singleton
 *    fun destinationConfig(): MyDestinationConfiguration =
 *      config as MyDestinationConfiguration
 *  }
 * ```
 *
 * Now your configuration will be automatically parsed and available for injection. ie,
 *
 * ```
 * @Singleton
 * class MyDestinationWriter(
 *   private val config: MyDestinationConfiguration // <- automatically injected by micronaut
 * ): DestinationWriter {
 * // ...
 * ```
 */
abstract class DestinationConfiguration : Configuration {
    // If this many seconds have passed without finishing data in flight, the framework will force
    // the workers to finish.
    open val maxTimeWithoutFlushingDataSeconds: Long =
        DEFAULT_MAX_TIME_WITHOUT_FLUSHING_DATA_SECONDS
    // How often to perform the above check.
    open val heartbeatIntervalSeconds: Long = DEFAULT_HEARTBEAT_INTERVAL_SECONDS

    /** Memory queue settings */
    open val maxMessageQueueMemoryUsageRatio: Double = 0.2 // 0 => No limit, 1.0 => 100% of JVM heap
    open val estimatedRecordMemoryOverheadRatio: Double =
        1.1 // 1.0 => No overhead, 2.0 => 100% overhead

    /**
     * The amount of time given to implementor tasks (e.g. open, processBatch) to complete their
     * current work after a failure. Input consuming will stop right away, so this will give the
     * tasks time to persist the messages already read.
     */
    open val gracefulCancellationTimeoutMs: Long = 10 * 60 * 1000L // 10 minutes

    /** How many calls to StreamLoader.start() can be in flight concurrently. */
    open val numOpenStreamWorkers: Int = 1

    companion object {
        const val DEFAULT_RECORD_BATCH_SIZE_BYTES = 200L * 1024L * 1024L
        const val DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 60L
        const val DEFAULT_MAX_TIME_WITHOUT_FLUSHING_DATA_SECONDS = 15 * 60L
        const val DEFAULT_GENERATION_ID_METADATA_KEY = "ab-generation-id"
    }

    // DEPRECATED: Old interface config. TODO: Drop when we're totally migrated.
    open val recordBatchSizeBytes: Long = DEFAULT_RECORD_BATCH_SIZE_BYTES
    open val processEmptyFiles: Boolean = false
    open val tmpFileDirectory: Path = Path.of("airbyte-cdk-load")
    open val numProcessRecordsWorkers: Int = 2
    open val numProcessBatchWorkers: Int = 5
    open val numProcessBatchWorkersForFileTransfer: Int = 3
    open val batchQueueDepth: Int = 10

    open val generationIdMetadataKey: String = DEFAULT_GENERATION_ID_METADATA_KEY

    /**
     * Micronaut factory which glues [ConfigurationSpecificationSupplier] and
     * [DestinationConfigurationFactory] together to produce a [DestinationConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationSpecification> destinationConfig(
            specificationSupplier: ConfigurationSpecificationSupplier<I>,
            factory: DestinationConfigurationFactory<I, out DestinationConfiguration>,
        ): DestinationConfiguration = factory.make(specificationSupplier.get())
    }
}
