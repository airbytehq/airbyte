/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import javax.inject.Singleton

@Singleton
@Primary
class MysqlJdbcStreamFactory(val base: JdbcAirbyteStreamFactory) : AirbyteStreamFactory by base {
    @Override
    override fun createGlobal(discoveredStream: DiscoveredStream): AirbyteStream {
        return AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            (jsonSchema["properties"] as ObjectNode).apply {
                for (metaField in MysqlCDCMetaFields.entries) {
                    set<ObjectNode>(metaField.id, metaField.type.airbyteSchemaType.asJsonSchema())
                }
            }
            if (base.hasValidPrimaryKey(discoveredStream)) {
                supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
                isResumable = true
                defaultCursorField = listOf(MysqlCDCMetaFields.CDC_CURSOR.id)
            } else {
                supportedSyncModes = listOf(SyncMode.FULL_REFRESH)
                isResumable = false
            }
        }
    }

    enum class MysqlCDCMetaFields(
        override val type: FieldType,
    ) : MetaField {
        CDC_CURSOR(CdcIntegerMetaFieldType),
        CDC_UPDATED_AT(CdcStringMetaFieldType),
        CDC_DELETED_AT(CdcStringMetaFieldType),
        CDC_LOG_POS(CdcIntegerMetaFieldType),
        CDC_LOG_FILE(CdcStringMetaFieldType),
        ;

        override val id: String
            get() = MetaField.META_PREFIX + name.lowercase()
    }
}
