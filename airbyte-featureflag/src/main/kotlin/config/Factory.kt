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
import jakarta.inject.Singleton
import java.nio.file.Path

internal const val CONFIG_LD_KEY = "airbyte.feature-flag.api-key"
internal const val CONFIG_OSS_KEY = "airbyte.feature-flag.path"

@Factory
class Factory {
    @Singleton
    fun featureFlagClient(
        @Property(name = CONFIG_LD_KEY) apiKey: String,
        @Property(name = CONFIG_OSS_KEY) configPath: String,
    ): FeatureFlagClient {
        // I cannot get the @Requires annotation to work to load one instance if a property is set and another instance if unset.
        // Combined both cases together here instead resulting to manually doing the is-set check via the isNotBlank function.
        if (apiKey.isNotBlank()) {
            val client = LDClient(apiKey)
            return LaunchDarklyClient(client)
        }

        val path: Path? = if (configPath.isNotBlank()) {
            Path.of(configPath)
        } else {
            null
        }
        return ConfigFileClient(path)
    }
}
