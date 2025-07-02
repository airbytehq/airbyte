/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2.operations

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.read.Stream
import io.airbyte.integrations.source.db2.Db2SourceCdcMetaFields
import io.airbyte.integrations.source.db2.TriggerTableConfig
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class Db2SourceStreamFactory : JdbcAirbyteStreamFactory {

    override val globalCursor: FieldOrMetaField = TriggerTableConfig.CURSOR_FIELD

    override val globalMetaFields: Set<MetaField> =
        setOf(
            Db2SourceCdcMetaFields.CHANGE_TIME,
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
            TriggerTableConfig.CURSOR_FIELD.id,
            null,
        )
    }
}
