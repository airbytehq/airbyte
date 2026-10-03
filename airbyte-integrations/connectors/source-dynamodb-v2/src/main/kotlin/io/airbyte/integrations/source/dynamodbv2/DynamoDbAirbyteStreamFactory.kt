/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/**
 * Builds the [AirbyteStream] of a DynamoDB table exactly like the legacy connector did:
 * - `FULL_REFRESH` and `INCREMENTAL` (user-defined cursor attribute) are supported by every table;
 * - the primary key is source-defined (the table's partition key), the cursor is not;
 * - the JSON schema is `{"type":"object","properties":{...}}` with the legacy per-attribute
 * schemas, which are built here because their shapes (`type` arrays, nested `properties`, `anyOf`
 * items) have no [io.airbyte.cdk.data.AirbyteSchemaType] equivalent.
 */
@Singleton
@Primary
class DynamoDbAirbyteStreamFactory : AirbyteStreamFactory {

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream,
    ): AirbyteStream {
        val properties: ObjectNode = Jsons.objectNode()
        for (field in discoveredStream.columns) {
            properties.set<JsonNode>(field.id, jsonSchema(field.type))
        }
        val jsonSchema: ObjectNode = Jsons.objectNode().put("type", "object")
        jsonSchema.set<JsonNode>("properties", properties)
        return AirbyteStream()
            .withName(discoveredStream.id.name)
            .withJsonSchema(jsonSchema)
            .withSupportedSyncModes(SUPPORTED_SYNC_MODES)
            .withSourceDefinedPrimaryKey(discoveredStream.primaryKeyColumnIDs)
    }

    private fun jsonSchema(type: FieldType): JsonNode =
        when (type) {
            is DynamoDbFieldType -> type.jsonSchema()
            else -> type.airbyteSchemaType.asJsonSchema()
        }

    companion object {
        val SUPPORTED_SYNC_MODES: List<SyncMode> =
            listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
    }
}
