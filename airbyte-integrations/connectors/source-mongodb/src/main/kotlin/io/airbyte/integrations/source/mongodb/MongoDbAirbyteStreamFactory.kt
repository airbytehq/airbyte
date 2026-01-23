/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.Field as AirbyteField
import io.airbyte.protocol.models.v0.SyncMode
import jakarta.inject.Singleton

/**
 * MongoDB implementation of [AirbyteStreamFactory].
 *
 * Creates [AirbyteStream] objects for discovered MongoDB collections.
 * Adds CDC metadata columns to match source-mongodb-v2 behavior.
 */
@Singleton
class MongoDbAirbyteStreamFactory : AirbyteStreamFactory {

    companion object {
        /** CDC metadata field for last update timestamp. */
        const val CDC_UPDATED_AT = "_ab_cdc_updated_at"

        /** CDC metadata field for deletion timestamp. */
        const val CDC_DELETED_AT = "_ab_cdc_deleted_at"

        /** CDC metadata field for cursor value. */
        const val CDC_DEFAULT_CURSOR = "_ab_cdc_cursor"
    }

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream {
        val hasPK = discoveredStream.primaryKeyColumnIDs.isNotEmpty()

        // MongoDB supports full refresh and incremental
        val syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)

        // Build the stream using our custom field mapping to get correct JsonSchemaType
        // for ARRAY and OBJECT types (bypassing the sealed AirbyteSchemaType interface)
        val stream = createMongoDbAirbyteStream(discoveredStream).apply {
            supportedSyncModes = syncModes
            sourceDefinedPrimaryKey = discoveredStream.primaryKeyColumnIDs
            // MongoDB uses CDC cursor for incremental syncs (matching v2 behavior)
            sourceDefinedCursor = true
            defaultCursorField = listOf(CDC_DEFAULT_CURSOR)
            isResumable = hasPK
        }

        // Add CDC metadata columns to the schema
        addCdcMetadataColumns(stream)

        return stream
    }

    /**
     * Creates an AirbyteStream using MongoDB-specific field type mapping.
     *
     * This method uses [MongoDbFieldType.jsonSchemaType] instead of
     * [AirbyteSchemaType.asJsonSchemaType] to correctly render ARRAY and OBJECT
     * types as {"type": "array"} and {"type": "object"} respectively.
     */
    private fun createMongoDbAirbyteStream(discoveredStream: DiscoveredStream): AirbyteStream {
        val fields = discoveredStream.columns.map { column ->
            val jsonSchemaType = when (val fieldType = column.type) {
                is MongoDbFieldType -> fieldType.jsonSchemaType
                else -> fieldType.airbyteSchemaType.asJsonSchemaType()
            }
            AirbyteField.of(column.id, jsonSchemaType)
        }

        return CatalogHelpers.createAirbyteStream(
            discoveredStream.id.name,
            discoveredStream.id.namespace,
            fields,
        )
    }

    /**
     * Adds CDC metadata columns to the stream's JSON schema.
     * Matches source-mongodb-v2 behavior.
     */
    private fun addCdcMetadataColumns(stream: AirbyteStream) {
        val jsonSchema = stream.jsonSchema as? ObjectNode ?: return
        val properties = jsonSchema.get("properties") as? ObjectNode ?: return

        // Add _ab_cdc_updated_at: string
        val stringType = Jsons.objectNode().put("type", "string")
        properties.set<ObjectNode>(CDC_UPDATED_AT, stringType)

        // Add _ab_cdc_deleted_at: string
        properties.set<ObjectNode>(CDC_DELETED_AT, Jsons.objectNode().put("type", "string"))

        // Add _ab_cdc_cursor: number with airbyte_type integer
        val cursorType = Jsons.objectNode()
            .put("type", "number")
            .put("airbyte_type", "integer")
        properties.set<ObjectNode>(CDC_DEFAULT_CURSOR, cursorType)
    }
}
