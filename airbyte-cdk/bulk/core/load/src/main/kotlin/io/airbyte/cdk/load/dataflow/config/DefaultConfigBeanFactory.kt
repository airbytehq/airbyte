/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.airbyte.cdk.load.dataflow.config.model.JsonConverterConfig
import io.airbyte.cdk.load.dataflow.config.model.LifecycleParallelismConfig
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Factory
class DefaultConfigBeanFactory {
    /** Provides default configuration for JsonConverter. */
    @Singleton
    @Secondary
    fun defaultJsonConvertConfig() =
        JsonConverterConfig(
            extractedAtAsTimestampWithTimezone = true,
        )

    /** Provides default configuration for Dispatchers used by DestinationLifecycle. */
    @Singleton @Secondary fun defaultLifecycleParallelismConfig() = LifecycleParallelismConfig()
}
