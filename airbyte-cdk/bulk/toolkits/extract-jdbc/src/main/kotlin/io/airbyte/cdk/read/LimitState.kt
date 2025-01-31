/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

/**
 * Adaptive LIMIT value state, where the value grows or shrinks along the Fibonacci sequence.
 *
 * This is a bit more gentle than doubling and halving.
 */
data class LimitState(
    val predecessor: Long,
    val current: Long,
) {
    /** Grow the LIMIT value. */
    val up: LimitState
        get() =
            if (predecessor > current) {
                LimitState(current, predecessor)
            } else {
                LimitState(current, current + predecessor)
            }

    /** Shrink the LIMIT value, if possible. */
    val down: LimitState
        get() =
            if (predecessor < current) {
                LimitState(current, predecessor)
            } else if (current == 1L) {
                this
            } else {
                LimitState(current, predecessor - current)
            }

    companion object {
        val minimum = LimitState(1L, 1L)
    }
}
