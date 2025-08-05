/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StateWatermarkStore(
    val watermarks: StateHistogram = StateHistogram(ConcurrentHashMap()),
    val expected: StateHistogram = StateHistogram(ConcurrentHashMap()),
) {
    private val log = KotlinLogging.logger {}

    fun acceptAggregateCounts(
        value: StateHistogram
    ): StateHistogram {
        return watermarks.merge(value)
    }

    fun acceptExpectedCounts(
        value: StateHistogram
    ): StateHistogram {
        return expected.merge(value)
    }
}
