/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import org.apache.kafka.connect.source.SourceRecord

// TODO: The T: Comparable<T> type here is used to determine when the target offset has been
//  reached. This doesn't actually require a well defined ordering on all offsets. In Postgres,
//  the criteria for stopping a sync do not result in a well-ordering of all offsets. As a result,
//  its implementation of compareTo(other: T) breaks the contract of compareTo(). To fix this,
//  we should define and use a weaker interface than Comparable with a method like:
//  fun hasReached(target: T): Boolean.
interface CdcPartitionReaderDebeziumOperations<T : Comparable<T>> {

    /**
     * Transforms a [DebeziumRecordKey] and a [DebeziumRecordValue] into a [DeserializedRecord].
     *
     * Returning null means that the event should be treated like a heartbeat.
     */
    fun deserializeRecord(
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

    /** Maps a Debezium state to an [OpaqueStateValue]. */
    fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?
    ): OpaqueStateValue

    /** Tries to extract the WAL position from a [DebeziumRecordValue]. */
    fun position(recordValue: DebeziumRecordValue): T?

    /** Tries to extract the WAL position from a [SourceRecord]. */
    fun position(sourceRecord: SourceRecord): T?
}
