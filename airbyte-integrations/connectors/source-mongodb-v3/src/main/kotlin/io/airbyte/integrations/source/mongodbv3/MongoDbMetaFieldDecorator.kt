/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LongCodec
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

/**
 * Adds the `_ab_cdc_*` meta fields to every stream schema and to every record, like the legacy
 * connector's `MongoDbCdcConnectorMetadataInjector`.
 *
 * MongoDB incremental syncs are CDC-only, so every stream carries these fields regardless of the
 * configured sync mode.
 */
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
     * Legacy cursor scheme for records read outside of the change stream: `emittedAt` epoch seconds
     * times 10^8 plus a counter starting at 1, shared by all streams of the sync.
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
        recordData.set<JsonNode>(
            MongoDbMetaField.CDC_CURSOR.id,
            Jsons.numberNode(nextCursor(timestamp))
        )
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
        recordData[MongoDbMetaField.CDC_CURSOR.id] =
            FieldValueEncoder(nextCursor(timestamp), LongCodec)
    }

    /**
     * Same format as the legacy connector: `Instant.toString()`, e.g. `2026-09-08T12:34:56.789Z`.
     */
    private fun updatedAt(timestamp: OffsetDateTime): String = timestamp.toInstant().toString()

    private fun nextCursor(timestamp: OffsetDateTime): Long {
        cursorBase.compareAndSet(0L, timestamp.toEpochSecond() * ONE_HUNDRED_MILLION)
        return cursorBase.get() + cursorCounter.getAndIncrement()
    }

    companion object {
        const val ONE_HUNDRED_MILLION = 100_000_000L
    }
}
