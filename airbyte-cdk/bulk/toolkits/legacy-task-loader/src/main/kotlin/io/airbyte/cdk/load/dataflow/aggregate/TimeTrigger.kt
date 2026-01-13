/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

/*
 * Encapsulates basic time-based windowing logic. As we implement other windowing,
 * we should look to break out a shared interface.
 */
class TimeTrigger(
    private val size: Long,
) {
    private var timestamp = 0L

    fun update(value: Long): TimeTrigger = this.apply { timestamp = value }

    fun isComplete(now: Long): Boolean = now - timestamp >= size
}
