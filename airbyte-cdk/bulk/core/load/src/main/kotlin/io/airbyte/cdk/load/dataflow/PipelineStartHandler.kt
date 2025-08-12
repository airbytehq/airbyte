/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class PipelineStartHandler(
    private val reconciler: StateReconciler,
) {
    private val log = KotlinLogging.logger {}

    fun run() {
        log.info { "Destination Pipeline Starting..." }

        reconciler.run()
    }
}
