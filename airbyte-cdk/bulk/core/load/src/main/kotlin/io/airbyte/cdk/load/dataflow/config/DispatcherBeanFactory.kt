/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.Clock
import java.time.Duration
import java.util.concurrent.Executors
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.asCoroutineDispatcher

/** The dispatchers (think views of thread pools) and static scopes we use for dataflow. */
@Factory
class DispatcherBeanFactory {
    @Named("pipelineRunnerDispatcher")
    @Singleton
    fun pipelineRunnerDispatcher() = Dispatchers.Default

    @Named("stateReconcilerDispatcher") @Singleton fun stateReconcilerDispatcher() = Dispatchers.IO

    @Named("aggregationDispatcher")
    @Singleton
    fun aggregationDispatcher(
        @Named("inputStreams") inputStreams: ConnectorInputStreams,
    ) = Executors.newFixedThreadPool(inputStreams.size).asCoroutineDispatcher()

    @Named("flushDispatcher") @Singleton fun flushDispatcher() = Dispatchers.IO

    @Named("pipelineRunnerScope")
    @Singleton
    fun pipelineRunnerDispatcher(
        @Named("pipelineRunnerDispatcher") dispatcher: CoroutineDispatcher,
    ) = CoroutineScope(dispatcher)

    @Named("stateReconcilerScope")
    @Singleton
    fun stateDispatcher(
        @Named("stateReconcilerDispatcher") dispatcher: CoroutineDispatcher,
    ) = CoroutineScope(dispatcher)

    @OptIn(ExperimentalCoroutinesApi::class)
    @Named("streamInitDispatcher")
    @Singleton
    fun streamInitDispatcher() = Dispatchers.Default.limitedParallelism(10)

    @OptIn(ExperimentalCoroutinesApi::class)
    @Named("streamFinalizeDispatcher")
    @Singleton
    fun streamFinalizeDispatcher() = Dispatchers.Default.limitedParallelism(10)

    /**
     * Optional threshold for detecting stalled sources (sources that have stopped emitting records).
     * Defaults to 10 minutes if not provided. Can be overridden by providing a Duration bean with this name.
     */
    @Named("sourceStallThreshold")
    @Singleton
    fun sourceStallThreshold(): Duration? = null

    /**
     * Clock for timestamp tracking. Defaults to system UTC clock.
     * Can be overridden for testing purposes.
     */
    @Singleton
    fun clock(): Clock = Clock.systemUTC()
}
