/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.Stream
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

    /**
     * Transforms a [DebeziumRecordKey] and a [DebeziumRecordValue] into a [DeserializedRecord].
     *
     * Returning null means that the event should be treated like a heartbeat.
     */
    fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord?

    /** Identifies the namespace of the stream that this event belongs to, if applicable. */
    fun findStreamNamespace(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
    ): String?

    /** Identifies the null of the stream that this event belongs to, if applicable. */
    fun findStreamName(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
    ): String?

    /** Maps a [DebeziumState] to an [OpaqueStateValue]. */
    fun serialize(debeziumState: DebeziumState): OpaqueStateValue

    /** Tries to extract the WAL position from a [DebeziumRecordValue]. */
    fun position(recordValue: DebeziumRecordValue): T?

    /** Tries to extract the WAL position from a [SourceRecord]. */
    fun position(sourceRecord: SourceRecord): T?
}

/** [DeserializedRecord]s are used to generate Airbyte RECORD messages. */
data class DeserializedRecord(
    val data: ObjectNode,
    val changes: Map<Field, FieldValueChange>,
)
