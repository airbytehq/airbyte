/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

typealias StateId = String

@Singleton
class StateWatermarkStore {

    private val log = KotlinLogging.logger {}

    private val watermarks = ConcurrentHashMap<StateId, StateHistogram>()

    fun accept(stateHistogram: StateHistogram) {
        log.debug { stateHistogram }
    }

    /*fun updateOrCreate(desc: StateId, stateHistogram: StateHistogram): StateHistogram {
        return watermarks.compute(desc) { _, w -> w?.merge(stateHistogram) ?: stateHistogram }!!
    }*/

    fun remove(desc: StateId): StateHistogram {
        return watermarks.computeIfPresent(desc) { _, _ -> null }!!
    }
}
