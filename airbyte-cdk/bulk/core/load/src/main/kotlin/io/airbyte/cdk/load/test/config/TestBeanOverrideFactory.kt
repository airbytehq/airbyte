/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.config

import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.dataflow.config.ConnectorInputStreams
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream
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
    // non-dockerized std-in acceptance tests create an input stream bean at runtime it uses
    // to send messages to the destination, so we must wire that up here
    @Requires(notEnv = ["docker"])
    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
    @Singleton
    @Primary
    @Named("inputStreams")
    fun testStdInStreams(
        @Named("inputStream") testInputStream: InputStream,
    ) = ConnectorInputStreams(listOf(testInputStream))

    @Singleton
    @Primary
    fun testConfig() =
        AggregatePublishingConfig(
            // Set this to 1 so we flush aggregates immediately for easier testing.
            maxRecordsPerAgg = 1,
        )

    @Singleton
    @Named("stateReconciliationInterval")
    fun stateReconciliationInterval() = 100.milliseconds.toJavaDuration()
}
