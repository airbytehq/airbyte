/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.CharacterStreamFieldType
import io.airbyte.cdk.jdbc.ClobFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.NCharacterStreamFieldType
import io.airbyte.cdk.jdbc.NClobFieldType
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import jakarta.inject.Singleton

@Singleton
class JdbcAirbyteStreamDecorator : AirbyteStreamDecorator {
    override fun decorateGlobal(airbyteStream: AirbyteStream) {
        airbyteStream.apply {
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            (jsonSchema["properties"] as ObjectNode).apply {
                for (metaField in CommonMetaField.entries) {
                    set<ObjectNode>(metaField.id, metaField.type.airbyteType.asJsonSchema())
                }
            }
            defaultCursorField = listOf(CommonMetaField.CDC_LSN.id)
            sourceDefinedCursor = true
        }
    }

    override fun decorateNonGlobal(airbyteStream: AirbyteStream) {
        airbyteStream.apply {
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
        }
    }

    override fun decorateNonGlobalNoCursor(airbyteStream: AirbyteStream) {
        airbyteStream.apply { supportedSyncModes = listOf(SyncMode.FULL_REFRESH) }
    }

    override fun isPossiblePrimaryKeyElement(field: Field): Boolean =
        when (field.type) {
            !is LosslessFieldType -> false
            BinaryStreamFieldType,
            CharacterStreamFieldType,
            NCharacterStreamFieldType,
            ClobFieldType,
            NClobFieldType,
            JsonStringFieldType, -> false
            else -> true
        }

    override fun isPossibleCursor(field: Field): Boolean =
        isPossiblePrimaryKeyElement(field) && field.type !is BooleanFieldType
}
