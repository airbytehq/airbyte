/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.discover

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import jakarta.inject.Singleton
import java.time.OffsetDateTime
import java.util.concurrent.atomic.AtomicLong

/** Adds the `_ab_cdc_*` meta fields to every stream and record (incremental is CDC-only). */
@Singleton
class MongoDbMetaFieldDecorator : MetaFieldDecorator {

    override val globalCursor: DataOrMetaField = MongoDbMetaField.CDC_CURSOR

    override val globalMetaFields: Set<MetaField> =
        setOf(
            CommonMetaField.CDC_UPDATED_AT,
            CommonMetaField.CDC_DELETED_AT,
            MongoDbMetaField.CDC_CURSOR,
        )

    /**
     * `_ab_cdc_cursor` is null on snapshot rows and `emittedAt` epoch milliseconds × 10^5 + a
     * per-sync counter on change events, stamped by the CDC reader through [nextCursor]: a change
     * always sorts above the snapshot row it supersedes (dedup ranks nulls last), change events
     * sort in event order, and later syncs start above earlier ones. The legacy formula was epoch
     * seconds × 10^8 — the same magnitude, so new values keep sorting above the rows it wrote.
     */
    private val cursorBase = AtomicLong(0L)
    private val cursorCounter = AtomicLong(1L)

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode,
    ) {
        recordData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            Jsons.textNode(updatedAt(timestamp))
        )
        recordData.set<JsonNode>(CommonMetaField.CDC_DELETED_AT.id, Jsons.nullNode())
        recordData.set<JsonNode>(MongoDbMetaField.CDC_CURSOR.id, Jsons.nullNode())
    }

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload,
    ) {
        recordData[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(updatedAt(timestamp), TextCodec)
        recordData[CommonMetaField.CDC_DELETED_AT.id] = FieldValueEncoder(null, NullCodec)
        recordData[MongoDbMetaField.CDC_CURSOR.id] = FieldValueEncoder(null, NullCodec)
    }

    private fun updatedAt(timestamp: OffsetDateTime): String = timestamp.toInstant().toString()

    fun nextCursor(timestamp: OffsetDateTime): Long {
        cursorBase.compareAndSet(0L, timestamp.toInstant().toEpochMilli() * CURSORS_PER_MILLI)
        return cursorBase.get() + cursorCounter.getAndIncrement()
    }

    companion object {
        const val CURSORS_PER_MILLI = 100_000L
    }
}
