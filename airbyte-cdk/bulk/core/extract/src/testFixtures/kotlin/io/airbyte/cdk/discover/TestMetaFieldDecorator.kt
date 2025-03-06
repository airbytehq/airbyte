/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Requires(env = [Environment.TEST])
@Requires(notEnv = [Environment.CLI])
class TestMetaFieldDecorator : MetaFieldDecorator {

    data object GlobalCursor : MetaField {
        override val id: String = MetaField.META_PREFIX + "cdc_lsn"
        override val type: FieldType = CdcStringMetaFieldType
    }

    override val globalCursor: MetaField = GlobalCursor

    override val globalMetaFields: Set<MetaField> =
        setOf(GlobalCursor, CommonMetaField.CDC_UPDATED_AT, CommonMetaField.CDC_DELETED_AT)

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        recordData.putNull(CommonMetaField.CDC_DELETED_AT.id)
        recordData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            CdcOffsetDateTimeMetaFieldType.jsonEncoder.encode(timestamp)
        )
        recordData.set<JsonNode>(
            GlobalCursor.id,
            if (globalStateValue == null) {
                Jsons.nullNode()
            } else {
                CdcStringMetaFieldType.jsonEncoder.encode(globalStateValue.toString())
            }
        )
    }
}
