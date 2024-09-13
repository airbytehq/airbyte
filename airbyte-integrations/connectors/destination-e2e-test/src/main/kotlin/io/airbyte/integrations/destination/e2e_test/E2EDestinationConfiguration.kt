/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class E2EDestinationConfiguration(
    val testDestination: TestDestination,
    override val recordBatchSizeBytes: Long = 1024L * 1024L,
    override val firstStageTmpFilePrefix: String =
        DestinationConfiguration.DEFAULT_FIRST_STAGE_TMP_FILE_PREFIX,
    override val maxMessageQueueMemoryUsageRatio: Double =
        DestinationConfiguration.DEFAULT_MAX_MESSAGE_QUEUE_MEMORY_USAGE_RATIO,
    override val estimatedRecordMemoryOverheadRatio: Double =
        DestinationConfiguration.DEFAULT_ESTIMATED_RECORD_MEMORY_OVERHEAD_RATIO
) : DestinationConfiguration

@Singleton
class E2EDestinationConfigurationFactory :
    DestinationConfigurationFactory<
        E2EDestinationConfigurationJsonObject, E2EDestinationConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: E2EDestinationConfigurationJsonObject
    ): E2EDestinationConfiguration {
        return E2EDestinationConfiguration(pojo.testDestination)
    }
}

@Factory
class E2EDestinationConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): E2EDestinationConfiguration {
        return config as E2EDestinationConfiguration
    }
}
