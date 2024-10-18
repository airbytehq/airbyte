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
    open val recordBatchSizeBytes: Long = 200L * 1024L * 1024L
    open val tmpFileDirectory: Path = Path.of("airbyte-cdk-load")
    open val firstStageTmpFilePrefix: String = "staged-raw-records"
    open val firstStageTmpFileSuffix: String = ".jsonl"

    /** Memory queue settings */
    open val maxMessageQueueMemoryUsageRatio: Double = 0.2 // 0 => No limit, 1.0 => 100% of JVM heap
    open val estimatedRecordMemoryOverheadRatio: Double =
        0.1 // 0 => No overhead, 1.0 => 100% overhead

    /**
     * If we have not flushed state checkpoints in this amount of time, make a best-effort attempt
     * to force a flush.
     */
    open val maxCheckpointFlushTimeMs: Long = 15 * 60 * 1000L // 15 minutes

    /** The max number of threads to use for implementor tasks (e.g. open, processBatch). */
    open val maxNumImplementorTaskThreads = 64

    /**
     * The amount of time given to implementor tasks (e.g. open, processBatch) to complete their
     * current work after a failure.
     */
    open val gracefulCancellationTimeoutMs: Long = 60 * 1000L // 1 minutes

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
