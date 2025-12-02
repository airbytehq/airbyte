/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.operations

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.TriggerCdcMetaFields
import io.airbyte.cdk.TriggerTableConfig
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class TriggerStreamFactory(private val config: TriggerTableConfig) : JdbcAirbyteStreamFactory {

    override val globalCursor: FieldOrMetaField = config.CURSOR_FIELD

    override val globalMetaFields: Set<MetaField> =
        setOf(
            TriggerCdcMetaFields.CHANGE_TIME,
            CommonMetaField.CDC_UPDATED_AT,
            CommonMetaField.CDC_DELETED_AT,
        )

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        recordData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            null,
        )
        recordData.set<JsonNode>(
            CommonMetaField.CDC_DELETED_AT.id,
            null,
        )
        recordData.set<JsonNode>(
            config.CURSOR_FIELD.id,
            null,
        )
    }

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {
        recordData[CommonMetaField.CDC_UPDATED_AT.id] = FieldValueEncoder(null, NullCodec)
        recordData[CommonMetaField.CDC_DELETED_AT.id] = FieldValueEncoder(null, NullCodec)
        recordData[config.CURSOR_FIELD.id] = FieldValueEncoder(null, NullCodec)
    }
}
