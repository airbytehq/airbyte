/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

data class LimitState(
    val predecessor: Long,
    val current: Long,
) {
    fun up(): LimitState =
        if (predecessor > current) {
            LimitState(current, predecessor)
        } else {
            LimitState(current, current + predecessor)
        }

    fun down(): LimitState =
        if (predecessor < current) {
            LimitState(current, predecessor)
        } else if (current == 1L) {
            this
        } else {
            LimitState(current, predecessor - current)
        }

    companion object {

        val minimum = LimitState(1L, 1L)

        val defaultProductionInitialValue: LimitState = run {
            var v = minimum
            for (i in 1..20) {
                v = v.up() // Corresponds to LimitState(6_765, 10_946)
            }
            return@run v
        }
    }
}
