/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2

import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

/** This is the simplified configuration object actually used by the implementation. */
sealed interface DevNull2Type

data class Logging(
    val maxEntryCount: Int,
    val logEvery: Int = 1,
    val sampleRate: Double = 1.0,
    val seed: Long? = null,
) : DevNull2Type

data object Silent : DevNull2Type

data class Failing(val numMessages: Int) : DevNull2Type

data class Throttled(val millisPerRecord: Long) : DevNull2Type

data class DevNull2Configuration(val type: DevNull2Type, val ackRatePerRecord: Int = 10_000) :
    DestinationConfiguration()

/**
 * This factory is injected into the initialization code and used to map from the client-provided
 * configuration json to the simplified configuration.
 *
 * Its role is to hide the complexities imposed by json-schema and the cloud/oss dichotomy from the
 * rest of the implementation.
 */
@Singleton
class DevNull2ConfigurationFactory :
    DestinationConfigurationFactory<DevNull2Specification, DevNull2Configuration> {

    override fun makeWithoutExceptionHandling(pojo: DevNull2Specification): DevNull2Configuration {
        return when (pojo) {
            is DevNull2SpecificationOss -> {
                when (pojo.testDestination) {
                    is LoggingDestination -> {
                        when (pojo.testDestination.loggingConfig) {
                            is FirstNEntriesConfig -> {
                                DevNull2Configuration(
                                    type =
                                        Logging(
                                            maxEntryCount =
                                                pojo.testDestination.loggingConfig.maxEntryCount
                                                    .toInt(),
                                        ),
                                )
                            }
                            is EveryNthEntryConfig -> {
                                DevNull2Configuration(
                                    type =
                                        Logging(
                                            maxEntryCount =
                                                pojo.testDestination.loggingConfig.maxEntryCount
                                                    .toInt(),
                                            logEvery =
                                                pojo.testDestination.loggingConfig.nthEntryToLog,
                                        )
                                )
                            }
                            is RandomSamplingConfig -> {
                                DevNull2Configuration(
                                    type =
                                        Logging(
                                            maxEntryCount =
                                                pojo.testDestination.loggingConfig.maxEntryCount
                                                    .toInt(),
                                            sampleRate =
                                                pojo.testDestination.loggingConfig.samplingRatio,
                                            seed = pojo.testDestination.loggingConfig.seed?.toLong()
                                        )
                                )
                            }
                        }
                    }
                    is SilentDestination -> {
                        DevNull2Configuration(type = Silent)
                    }
                    is ThrottledDestination -> {
                        DevNull2Configuration(
                            type = Throttled(pojo.testDestination.millisPerRecord)
                        )
                    }
                    is FailingDestination -> {
                        DevNull2Configuration(type = Failing(pojo.testDestination.numMessages))
                    }
                }
            }
            is DevNull2SpecificationCloud -> {
                when (pojo.testDestination) {
                    is SilentDestinationCloud -> {
                        DevNull2Configuration(type = Silent)
                    }
                }
            }
        }
    }
}

/** Bean factory providing configuration instances via Micronaut DI. */
@Factory
class DevNull2BeanFactory {
    @Singleton
    fun devNull2Configuration(
        configFactory: DevNull2ConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<DevNull2Specification>,
    ): DevNull2Configuration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    fun tempTableNameGenerator(): io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator =
        io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator()

    @Singleton
    fun aggregatePublishingConfig(): io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig =
        io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000_000L,
            maxEstBytesPerAgg = 350_000_000L,
            maxEstBytesAllAggregates = 350_000_000L * 5,
        )
}
