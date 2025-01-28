/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

/** This is the simplified configuration object actually used by the implementation. */
sealed interface DevNullType

data class Logging(
    val maxEntryCount: Int,
    val logEvery: Int = 1,
    val sampleRate: Double = 1.0,
    val seed: Long? = null,
) : DevNullType

data object Silent : DevNullType

data class Failing(val numMessages: Int) : DevNullType

data class Throttled(val millisPerRecord: Long) : DevNullType

data class DevNullConfiguration(
    val type: DevNullType,
    override val skipStreamLoading: Boolean = false
) : DestinationConfiguration()

/**
 * This factory is injected into the initialization code and used to map from the client-provided
 * configuration json to the simplified configuration.
 *
 * Its role is to hide the complexities imposed by json-schema and the cloud/oss dichotomy from the
 * rest of the implementation.
 */
@Singleton
class DevNullConfigurationFactory :
    DestinationConfigurationFactory<DevNullSpecification, DevNullConfiguration> {
    private val log = KotlinLogging.logger {}

    override fun makeWithoutExceptionHandling(pojo: DevNullSpecification): DevNullConfiguration {
        return when (pojo) {
            is DevNullSpecificationOss -> {
                when (pojo.testDestination) {
                    is LoggingDestination -> {
                        when (pojo.testDestination.loggingConfig) {
                            is FirstNEntriesConfig -> {
                                DevNullConfiguration(
                                    type =
                                        Logging(
                                            maxEntryCount =
                                                pojo.testDestination.loggingConfig.maxEntryCount
                                                    .toInt(),
                                        ),
                                )
                            }
                            is EveryNthEntryConfig -> {
                                DevNullConfiguration(
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
                                DevNullConfiguration(
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
                        DevNullConfiguration(type = Silent)
                    }
                    is ThrottledDestination -> {
                        DevNullConfiguration(type = Throttled(pojo.testDestination.millisPerRecord))
                    }
                    is FailingDestination -> {
                        DevNullConfiguration(type = Failing(pojo.testDestination.numMessages))
                    }
                }
            }
            is DevNullSpecificationCloud -> {
                when (pojo.testDestination) {
                    is SilentDestinationCloud -> {
                        DevNullConfiguration(type = Silent, skipStreamLoading = true)
                    }
                }
            }
        }
    }
}

/** This allows micronaut to inject the simplified configuration into the implementation. */
@Factory
class DevNullConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): DevNullConfiguration {
        return config as DevNullConfiguration
    }
}
