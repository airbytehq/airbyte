/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import org.apache.kafka.connect.source.SourceRecord

/**
 * [CdcPositionMapper] abstracts the mapping from states and records to a database-dependent Cdc
 * position value. All that matters as far as anything is concerned is that the values are
 * [Comparable].
 */
interface CdcPositionMapper<T : Comparable<T>> {

    /** Maps a [DebeziumState.Offset] to an LSN value. */
    fun get(offset: DebeziumState.Offset): T

    /** Maps a [Record] to an Cdc position value. */
    fun get(record: DebeziumRecord): T?

    /** Maps a [SourceRecord] to an Cdc position value. */
    fun get(sourceRecord: SourceRecord): T?

    /** [asAny] makes it possible to compare the outputs of [CdcPositionMapper]<*>. */
    @Suppress("UNCHECKED_CAST")
    fun asAny(): CdcPositionMapper<Comparable<Any>> = this as CdcPositionMapper<Comparable<Any>>

    fun comparator(): Comparator<DebeziumState> = Comparator { before, after ->
        asAny().get(before!!.offset).compareTo(asAny().get(after!!.offset))
    }
}
