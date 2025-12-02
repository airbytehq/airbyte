/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component.config

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.util.Jsons
import java.nio.file.Files
import kotlin.io.path.Path
import kotlin.reflect.full.createInstance

/** Utility object for loading test configuration from secrets files. */
object TestConfigLoader {
    fun <
        T : DestinationConfiguration,
        U : ConfigurationSpecification,
        V : DestinationConfigurationFactory<in U, out T>,
    > loadTestConfig(
        specClass: Class<U>,
        factoryClass: Class<V>,
        configPath: String,
    ): T {
        val configStr = Files.readString(Path("secrets/$configPath"))
        val spec = Jsons.readValue(configStr, specClass)
        val factory = factoryClass.kotlin.createInstance()

        return factory.makeWithoutExceptionHandling(spec)
    }
}
