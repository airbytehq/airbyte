/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag.config

import com.launchdarkly.sdk.server.LDClient
import io.airbyte.featureflag.Client
import io.airbyte.featureflag.Cloud
import io.airbyte.featureflag.Platform
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requirements
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.nio.file.Path

internal const val CONFIG_LD_KEY = "airbyte.feature-flag.api-key"
internal const val CONFIG_OSS_KEY = "airbyte.feature-flag.path"

@Factory
class Factory {
    @Requirements(
        Requires(property = CONFIG_LD_KEY),
        Requires(missingProperty = CONFIG_OSS_KEY),
    )
    @Singleton
    fun Cloud(@Property(name = CONFIG_LD_KEY) apiKey: String): Client {
        val client = LDClient(apiKey)
        return Cloud(client)
    }

    @Requirements(
        Requires(property = CONFIG_OSS_KEY),
        Requires(missingProperty = CONFIG_LD_KEY),
    )
    fun Platform(@Property(name = CONFIG_OSS_KEY) configPath: String): Client {
        val path = Path.of(configPath)
        return Platform(path)
    }
}