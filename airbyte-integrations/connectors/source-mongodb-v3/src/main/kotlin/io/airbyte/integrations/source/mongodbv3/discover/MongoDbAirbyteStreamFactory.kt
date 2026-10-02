/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.discover

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/**
 * Builds the [AirbyteStream] of a collection: `FULL_REFRESH` and `INCREMENTAL` (change stream), a
 * source-defined `_ab_cdc_cursor` cursor, `_id` as primary key, resumable, with the `_ab_cdc_*`
 * meta fields. The JSON schema is built here rather than with
 * [AirbyteStreamFactory.createAirbyteStream] because the per-type schemas (`{"type":"array"}`
 * without `items`, plain `{"type":"object"}`) have no exact [io.airbyte.cdk.data.AirbyteSchemaType]
 * equivalent.
 */
@Singleton
@Primary
class MongoDbAirbyteStreamFactory(
    private val metaFieldDecorator: MetaFieldDecorator,
) : AirbyteStreamFactory {

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream {
        val properties: ObjectNode = Jsons.objectNode()
        for (field in discoveredStream.columns) {
            properties.set<JsonNode>(field.id, jsonSchema(field.type))
        }
        for (metaField in metaFieldDecorator.globalMetaFields) {
            properties.set<JsonNode>(metaField.id, jsonSchema(metaField.type))
        }
        val jsonSchema: ObjectNode = Jsons.objectNode().put("type", "object")
        jsonSchema.set<JsonNode>("properties", properties)
        return AirbyteStream()
            .withName(discoveredStream.id.name)
            .withNamespace(discoveredStream.id.namespace)
            .withJsonSchema(jsonSchema)
            .withSupportedSyncModes(SUPPORTED_SYNC_MODES)
            .withSourceDefinedCursor(true)
            .withDefaultCursorField(listOfNotNull(metaFieldDecorator.globalCursor?.id))
            .withSourceDefinedPrimaryKey(discoveredStream.primaryKeyColumnIDs)
            .withIsResumable(true)
    }

    private fun jsonSchema(type: FieldType): JsonNode =
        when (type) {
            is MongoDbFieldType -> type.jsonSchema()
            else -> type.airbyteSchemaType.asJsonSchema()
        }

    companion object {
        val SUPPORTED_SYNC_MODES: List<SyncMode> =
            listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
    }
}
