/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class DevNullV2Configuration(
    val type: Type,
    val logEvery: Int = 1,
    val maxEntryCount: Int = 1000,
    val sampleRate: Double = 1.0,
    val seed: Long? = null,
    val millisPerRecord: Long = 0,
    val numMessages: Int = 0
) : DestinationConfiguration() {
    enum class Type {
        LOGGING,
        SILENT,
        THROTTLED,
        FAILING
    }
}

@Singleton
class DevNullV2ConfigurationFactory :
    DestinationConfigurationFactory<DevNullV2Specification, DevNullV2Configuration> {

    private val log = KotlinLogging.logger {}

    override fun makeWithoutExceptionHandling(
        pojo: DevNullV2Specification
    ): DevNullV2Configuration {
        return when (val destination = pojo.testDestination) {
            is LoggingDestination -> {
                val config = destination.loggingConfig
                when (config) {
                    is FirstNEntriesConfig -> {
                        log.info {
                            "Creating LOGGING configuration with FirstN, maxEntryCount: ${config.maxEntryCount}"
                        }
                        DevNullV2Configuration(
                            type = DevNullV2Configuration.Type.LOGGING,
                            logEvery = 1,
                            maxEntryCount = config.maxEntryCount.toInt()
                        )
                    }
                    is EveryNthEntryConfig -> {
                        log.info {
                            "Creating LOGGING configuration with EveryNth, nthEntry: ${config.nthEntryToLog}, maxEntryCount: ${config.maxEntryCount}"
                        }
                        DevNullV2Configuration(
                            type = DevNullV2Configuration.Type.LOGGING,
                            logEvery = config.nthEntryToLog,
                            maxEntryCount = config.maxEntryCount.toInt()
                        )
                    }
                    is RandomSamplingConfig -> {
                        log.info {
                            "Creating LOGGING configuration with RandomSampling, ratio: ${config.samplingRatio}, maxEntryCount: ${config.maxEntryCount}"
                        }
                        DevNullV2Configuration(
                            type = DevNullV2Configuration.Type.LOGGING,
                            sampleRate = config.samplingRatio,
                            seed = config.seed?.toLong(),
                            maxEntryCount = config.maxEntryCount.toInt()
                        )
                    }
                }
            }
            is SilentDestination -> {
                log.info { "Creating SILENT configuration" }
                DevNullV2Configuration(type = DevNullV2Configuration.Type.SILENT)
            }
            is ThrottledDestination -> {
                log.info {
                    "Creating THROTTLED configuration with millisPerRecord: ${destination.millisPerRecord}"
                }
                DevNullV2Configuration(
                    type = DevNullV2Configuration.Type.THROTTLED,
                    millisPerRecord = destination.millisPerRecord
                )
            }
            is FailingDestination -> {
                log.info {
                    "Creating FAILING configuration with numMessages: ${destination.numMessages}"
                }
                DevNullV2Configuration(
                    type = DevNullV2Configuration.Type.FAILING,
                    numMessages = destination.numMessages
                )
            }
            is SilentDestinationCloud -> {
                log.info { "Creating SILENT configuration (cloud)" }
                DevNullV2Configuration(type = DevNullV2Configuration.Type.SILENT)
            }
            else -> {
                log.warn { "Unknown destination type, defaulting to SILENT" }
                DevNullV2Configuration(type = DevNullV2Configuration.Type.SILENT)
            }
        }
    }
}

@Factory
class DevNullV2ConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): DevNullV2Configuration {
        return config as DevNullV2Configuration
    }
}
