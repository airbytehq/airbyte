/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.config

import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.toJavaDuration

/**
 * Why is this not in a test package?
 *
 * We have to include this in the source so it's built in the docker image for the docker tests.
 */
@Factory
@Requires(env = [Environment.TEST])
class TestBeanOverrideFactory {
    @Singleton
    @Primary
    fun testConfig() =
        MemoryAndParallelismConfig(
            // Set this to 1 so we flush aggregates immediately for easier testing.
            maxRecordsPerAgg = 1,
        )

    @Singleton
    @Named("stateReconciliationInterval")
    fun stateReconciliationInterval() = 100.milliseconds.toJavaDuration()
}
