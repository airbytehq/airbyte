/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.Clock
import java.time.Duration

/** Factory for message flow monitoring configuration beans. */
@Factory
class MessageFlowMonitoringBeanFactory {

    /**
     * Threshold for detecting stalled sources (sources that have stopped emitting records).
     * When the time since the last message exceeds this threshold, a warning is logged.
     * Defaults to 10 minutes if not provided.
     */
    @Named("sourceStallThreshold")
    @Singleton
    fun sourceStallThreshold(): Duration? = null

    /**
     * Clock for timestamp operations in message watermark tracking.
     * Defaults to system UTC clock. Can be overridden for testing purposes.
     */
    @Singleton
    fun clock(): Clock = Clock.systemUTC()
}
