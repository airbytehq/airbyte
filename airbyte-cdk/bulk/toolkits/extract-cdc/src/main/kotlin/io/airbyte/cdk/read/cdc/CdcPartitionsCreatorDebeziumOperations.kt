/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream

// TODO: The T: Comparable<T> type here is used to determine when the target offset has been
//  reached. This doesn't actually require a well defined ordering on all offsets. In Postgres,
//  the criteria for stopping a sync do not result in a well-ordering of all offsets. As a result,
//  the implementation of compareTo(other: T) breaks the contract of compareTo(). To fix this,
//  we should define and use a weaker interface than Comparable with a method like:
//  fun hasReached(t: T): Boolean.
interface CdcPartitionsCreatorDebeziumOperations<T : Comparable<T>> {

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
