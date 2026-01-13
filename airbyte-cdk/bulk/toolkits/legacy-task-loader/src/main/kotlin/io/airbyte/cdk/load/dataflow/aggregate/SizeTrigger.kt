/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

/*
 * Encapsulates basic size-based windowing logic. As we implement other windowing,
 * we should look to break out a shared interface.
 */
class SizeTrigger(private val size: Long) {
    private var accumulated = 0L

    fun increment(quantity: Long): SizeTrigger = this.apply { accumulated += quantity }

    fun watermark() = accumulated

    fun isComplete(): Boolean = accumulated >= size
}
