/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import org.apache.kafka.connect.source.SourceRecord

/**
 * [LsnMapper] abstracts the mapping from states and records to a database-dependent LSN value. All
 * that matters as far as anything is concerned is that the values are [Comparable].
 */
@JvmDefaultWithCompatibility
interface LsnMapper<T : Comparable<T>> {

    /** Maps a [DebeziumState.Offset] to an LSN value. */
    fun get(offset: DebeziumState.Offset): T

    /** Maps a [Record] to an LSN value. */
    fun get(record: DebeziumRecord): T?

    /** Maps a [SourceRecord] to an LSN value. */
    fun get(sourceRecord: SourceRecord): T?

    /** [asAny] makes it possible to compare the outputs of [LsnMapper]<*>. */
    @Suppress("UNCHECKED_CAST")
    fun asAny(): LsnMapper<Comparable<Any>> = this as LsnMapper<Comparable<Any>>

    fun comparator(): Comparator<DebeziumState> = Comparator { before, after ->
        asAny().get(before!!.offset).compareTo(asAny().get(after!!.offset))
    }
}
