/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping.migrators

/**
 * All destination states MUST contain a parameter `needsSoftReset`. This allows migrators to track
 * whether a soft reset is necessary, and persist that value across syncs in case of sync failure.
 */
interface MinimumDestinationState {
    fun needsSoftReset(): Boolean

    /**
     * The type parameter should be the subclass itself. We need this so that [withSoftReset] can
     * return the correct type. Callers are responsible for passing the correct type parameter into
     * this function (e.g. `currentState.withSoftReset<DestinationState>(softReset)`).
     *
     * Implementations generally look like this: (note the unchecked `as T` cast)
     * ```kotlin
     * data class ExampleState(val needsSoftReset: Boolean, <other fields...>): MinimumDestinationState {
     *   override fun needsSoftReset(): Boolean {
     *     return needsSoftReset
     *   }
     *
     *   override fun <T: MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T {
     *     return copy(needsSoftReset = true) as T
     *   }
     * }
     * ```
     */
    fun <T : MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T

    /**
     * A minimal implementation of [MinimumDestinationState]. This is useful for destinations that
     * don't want to bother implementing a full state object.
     */
    data class Impl(val needsSoftReset: Boolean) : MinimumDestinationState {
        override fun needsSoftReset(): Boolean {
            return needsSoftReset
        }

        @Suppress("UNCHECKED_CAST")
        override fun <T : MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T {
            return Impl(needsSoftReset = needsSoftReset) as T
        }
    }
}
