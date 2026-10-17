/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

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
 * Builds the [AirbyteStream] of a MongoDB collection, exactly like the legacy connector's
 * `MongoCatalogHelper`:
 * - `FULL_REFRESH` and `INCREMENTAL` (change stream CDC) are supported by every collection;
 * - the cursor is source-defined (`_ab_cdc_cursor`) and the primary key is always `_id`;
 * - every stream is resumable and carries the `_ab_cdc_*` meta fields;
 * - the JSON schema is `{"type":"object","properties":{...}}` with the legacy per-type schemas.
 *
 * The JSON schema is built here rather than with [AirbyteStreamFactory.createAirbyteStream] because
 * the legacy schemas (`{"type":"array"}` without `items`, `{"type":"object"}`) have no exact
 * [io.airbyte.cdk.data.AirbyteSchemaType] equivalent.
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
