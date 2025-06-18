/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write

/*
 * Encapsulates basic sized windowing logic. As we implement other windowing,
 * we should look to break out a shared interface.
 */
class SizedWindow(private val size: Long) {
    private var accumulated = 0L

    fun increment(quantity: Long): SizedWindow = this.apply { accumulated += quantity }

    fun isComplete(): Boolean = accumulated >= size
}
