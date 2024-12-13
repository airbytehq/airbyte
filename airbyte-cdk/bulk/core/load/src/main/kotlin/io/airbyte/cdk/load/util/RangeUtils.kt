/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import com.google.common.collect.Range

// Necessary because Guava's Range/sets have no "empty" range
fun Range<Long>?.withNextAdjacentValue(index: Long): Range<Long> {
    return if (this == null) {
        Range.singleton(index)
    } else if (index != this.upperEndpoint() + 1L) {
        throw IllegalStateException("Expected index ${this.upperEndpoint() + 1}, got $index")
    } else {
        this.span(Range.singleton(index))
    }
}
