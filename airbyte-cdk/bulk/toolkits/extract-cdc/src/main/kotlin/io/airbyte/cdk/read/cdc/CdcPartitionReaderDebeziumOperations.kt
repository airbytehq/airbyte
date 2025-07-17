/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import org.apache.kafka.connect.source.SourceRecord

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
