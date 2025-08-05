/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StateWatermarkStore(
    private val watermarks: StateHistogram = StateHistogram(ConcurrentHashMap()),
    private val expected: StateHistogram = StateHistogram(ConcurrentHashMap()),
) {
    fun accept(
        value: StateHistogram
    ): StateHistogram {
        return watermarks.merge(value)
    }
}
