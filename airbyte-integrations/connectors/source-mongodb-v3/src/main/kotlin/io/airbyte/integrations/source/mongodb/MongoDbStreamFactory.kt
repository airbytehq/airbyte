/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcOffsetDateTimeMetaFieldType
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import javax.inject.Singleton

@Singleton
@Primary
class MongoDbStreamFactory : AirbyteStreamFactory {
    @Override
    override fun createGlobal(discoveredStream: DiscoveredStream): AirbyteStream {
        return AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
            (jsonSchema["properties"] as ObjectNode).apply {
                for (metaField in MongoDbCDCMetaFields.entries) {
                    set<ObjectNode>(metaField.id, metaField.type.airbyteSchemaType.asJsonSchema())
                }
            }
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
            sourceDefinedCursor = true
            isResumable = true
            defaultCursorField = listOf(MongoDbCDCMetaFields.CDC_CURSOR.id)
        }
    }

    override fun createNonGlobal(discoveredStream: DiscoveredStream): AirbyteStream {
        TODO("Not yet implemented")
    }

    enum class MongoDbCDCMetaFields(
        override val type: FieldType,
    ) : MetaField {
        CDC_CURSOR(CdcIntegerMetaFieldType),
        CDC_UPDATED_AT(CdcOffsetDateTimeMetaFieldType),
        CDC_DELETED_AT(CdcOffsetDateTimeMetaFieldType),
        ;

        override val id: String
            get() = MetaField.META_PREFIX + name.lowercase()
    }
}
