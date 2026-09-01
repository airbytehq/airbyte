/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
class MongoDbMetaFieldDecorator : MetaFieldDecorator {

    override val globalCursor: FieldOrMetaField = MongoDbCdcMetaFields.CDC_CURSOR

    override val globalMetaFields: Set<MetaField> = setOf(
        CommonMetaField.CDC_UPDATED_AT,
        CommonMetaField.CDC_DELETED_AT,
        MongoDbCdcMetaFields.CDC_CURSOR,
    )

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        // No-op for full refresh; will be implemented for CDC/incremental.
    }

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {
        // No-op for full refresh; will be implemented for CDC/incremental.
    }
}
