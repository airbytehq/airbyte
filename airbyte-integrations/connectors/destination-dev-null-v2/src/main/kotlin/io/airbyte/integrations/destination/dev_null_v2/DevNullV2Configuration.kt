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
    val mode: String = "silent",
    val logEveryN: Int = 1000
) : DestinationConfiguration()

@Singleton
class DevNullV2ConfigurationFactory :
    DestinationConfigurationFactory<DevNullV2Specification, DevNullV2Configuration> {
    
    private val log = KotlinLogging.logger {}

    override fun makeWithoutExceptionHandling(pojo: DevNullV2Specification): DevNullV2Configuration {
        log.info { "Creating configuration with mode: ${pojo.mode}, logEveryN: ${pojo.logEveryN}" }
        return DevNullV2Configuration(
            mode = pojo.mode,
            logEveryN = pojo.logEveryN
        )
    }
}

@Factory
class DevNullV2ConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): DevNullV2Configuration {
        return config as DevNullV2Configuration
    }
}