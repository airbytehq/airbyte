/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.AirbyteValueJsonlProxy
import io.airbyte.cdk.load.data.AirbyteValueProtobufProxy
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.asJson
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf

/**
 * A serialization-format agnostic wrapper for incoming [DestinationRecord]'s. The record-level
 * corollary to [io.airbyte.cdk.load.data.AirbyteValueProxy], providing uniform access to both
 * client data and metadata.
 */
sealed interface DestinationRecordSource {
    val emittedAtMs: Long
    val sourceMeta: Meta
    val fileReference: FileReference?
    fun asJsonRecord(orderedSchema: Array<FieldAccessor>): JsonNode
    fun asAirbyteValueProxy(): AirbyteValueProxy
}

@JvmInline
value class DestinationRecordJsonSource(val source: AirbyteMessage) : DestinationRecordSource {
    override val emittedAtMs: Long
        get() = source.record.emittedAt
    override val sourceMeta: Meta
        get() =
            Meta(
                changes =
                    source.record.meta?.changes?.map { change ->
                        Meta.Change(
                            field = change.field,
                            change = change.change,
                            reason = change.reason,
                        )
                    }
                        ?: emptyList()
            )

    override val fileReference: FileReference?
        get() = source.record.fileReference?.let { FileReference.fromProtocol(it) }

    override fun asJsonRecord(orderedSchema: Array<FieldAccessor>): JsonNode = source.record.data

    override fun asAirbyteValueProxy(): AirbyteValueProxy =
        AirbyteValueJsonlProxy(source.record.data as ObjectNode)
}

@JvmInline
value class DestinationRecordProtobufSource(val source: AirbyteMessageProtobuf) :
    DestinationRecordSource {
    override val emittedAtMs: Long
        get() = source.record.emittedAtMs
    override val sourceMeta: Meta
        get() =
            Meta(
                changes =
                    source.record.meta?.changesList?.map { change ->
                        Meta.Change(
                            field = change.field,
                            change = Change.fromValue(change.change.name),
                            reason = Reason.fromValue(change.reason.name)
                        )
                    }
                        ?: emptyList()
            )

    override val fileReference: FileReference?
        get() = null

    override fun asJsonRecord(orderedSchema: Array<FieldAccessor>): JsonNode =
        asAirbyteValueProxy().asJson(orderedSchema)

    override fun asAirbyteValueProxy(): AirbyteValueProxy =
        AirbyteValueProtobufProxy(source.record.dataList)
}
