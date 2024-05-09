/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.global

import io.airbyte.cdk.read.CdcCompleted
import io.airbyte.cdk.read.CdcNotStarted
import io.airbyte.cdk.read.CdcOngoing
import io.airbyte.cdk.read.CdcStarting
import io.airbyte.cdk.read.GlobalKey
import io.airbyte.cdk.read.GlobalState
import io.airbyte.cdk.read.Worker
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton

/** Generates a [Worker] to make progress on a [GlobalState]. */
@DefaultImplementation(DefaultGlobalWorkerFactory::class)
fun interface GlobalWorkerFactory {

    fun make(input: GlobalState): Worker<GlobalKey, out GlobalState>?
}

/**
 * Sane default implementation of [GlobalWorkerFactory].
 *
 * Some connectors may choose to substitute this for their own implementation.
 */
@Singleton
class DefaultGlobalWorkerFactory : GlobalWorkerFactory {

    override fun make(input: GlobalState): Worker<GlobalKey, out GlobalState>? =
        when (input) {
            is CdcCompleted -> null
            is CdcOngoing -> CdcOngoingWorker(input)
            is CdcStarting -> CdcWarmStartWorker(input)
            is CdcNotStarted -> CdcColdStartWorker(input)
        }
}
