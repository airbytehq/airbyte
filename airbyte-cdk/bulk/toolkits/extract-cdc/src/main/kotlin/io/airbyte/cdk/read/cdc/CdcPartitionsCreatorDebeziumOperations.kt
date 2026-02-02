/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream

interface CdcPartitionsCreatorDebeziumOperations<T : PartiallyOrdered<T>> {

    companion object {
        @Volatile private var hasRunStartup = false
        @Synchronized
        fun shouldRunStartup(): Boolean {
            if (!hasRunStartup) {
                hasRunStartup = true
                return true
            }
            return false
        }
    }

    /** Run optional startup hook if it hasn't already been run */
    fun runStartup(offset: DebeziumOffset) {
        if (shouldRunStartup()) {
            startup(offset)
        }
    }

    /** Optional startup hook. */
    fun startup(offset: DebeziumOffset) {}

    /** Extracts the WAL position from a [DebeziumOffset]. */
    fun position(offset: DebeziumOffset): T

    /**
     * Synthesizes a [DebeziumColdStartingState] when no incumbent [OpaqueStateValue] is available.
     */
    fun generateColdStartOffset(): DebeziumOffset

    /** Generates Debezium properties for use with a [DebeziumColdStartingState]. */
    fun generateColdStartProperties(streams: List<Stream>): Map<String, String>

    /** Maps an incumbent [OpaqueStateValue] into a [DebeziumWarmStartState]. */
    fun deserializeState(opaqueStateValue: OpaqueStateValue): DebeziumWarmStartState

    /** Generates Debezium properties for use with a [ValidDebeziumWarmStartState]. */
    fun generateWarmStartProperties(streams: List<Stream>): Map<String, String>
}
