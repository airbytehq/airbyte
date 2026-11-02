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

    // `_ab_cdc_cursor` (MongoDB cluster time: sync start for a snapshot row, the event's time for
    // a change) is stamped per record by the readers; the default record only carries null.
    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode,
    ) {
        recordData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            Jsons.textNode(updatedAt(timestamp)),
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
}
