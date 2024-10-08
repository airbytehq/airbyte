/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import org.apache.kafka.connect.source.SourceRecord

/** Stateless connector-specific Debezium operations. */
interface DebeziumOperations<T : Comparable<T>> :
    CdcPartitionsCreatorDebeziumOperations<T>, CdcPartitionReaderDebeziumOperations<T>

interface CdcPartitionsCreatorDebeziumOperations<T : Comparable<T>> {

    /** Extracts the WAL position from a [DebeziumOffset]. */
    fun position(offset: DebeziumOffset): T

    /** Synthesizes a [DebeziumInput] when no incumbent [OpaqueStateValue] is available. */
    fun synthesize(): DebeziumInput

    /** Builds a [DebeziumInput] using an incumbent [OpaqueStateValue]. */
    fun deserialize(opaqueStateValue: OpaqueStateValue, streams: List<Stream>): DebeziumInput
}

interface CdcPartitionReaderDebeziumOperations<T : Comparable<T>> {

    /** Transforms a [DebeziumRecordValue] into an [AirbyteRecordMessage]. */
    fun toAirbyteRecordMessage(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue
    ): AirbyteRecordMessage

    /** Maps a [DebeziumState] to an [OpaqueStateValue]. */
    fun serialize(debeziumState: DebeziumState): OpaqueStateValue

    /** Tries to extract the WAL position from a [DebeziumRecordValue]. */
    fun position(recordValue: DebeziumRecordValue): T?

    /** Tries to extract the WAL position from a [SourceRecord]. */
    fun position(sourceRecord: SourceRecord): T?
}
