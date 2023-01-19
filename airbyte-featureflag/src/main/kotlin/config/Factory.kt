/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag.config

import com.launchdarkly.sdk.server.LDClient
import io.airbyte.featureflag.ConfigFileClient
import io.airbyte.featureflag.FeatureFlagClient
import io.airbyte.featureflag.LaunchDarklyClient
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.nio.file.Path

internal const val CONFIG_LD_KEY = "airbyte.feature-flag.api-key"
internal const val CONFIG_OSS_KEY = "airbyte.feature-flag.path"

@Factory
class Factory {

    @Requires(property = CONFIG_LD_KEY)
    @Singleton
    fun LaunchDarklyClient(@Property(name = CONFIG_LD_KEY) apiKey: String): FeatureFlagClient {
        val client = LDClient(apiKey)
        return LaunchDarklyClient(client)
    }

    @Requires(missingProperty = CONFIG_LD_KEY)
    @Singleton
    fun ConfigFileClient(@Property(name = CONFIG_OSS_KEY) configPath: String): FeatureFlagClient {
        val path: Path? = if (configPath.isNotBlank()) {
            Path.of(configPath)
        } else {
            null
        }
        return ConfigFileClient(path)
    }
}
