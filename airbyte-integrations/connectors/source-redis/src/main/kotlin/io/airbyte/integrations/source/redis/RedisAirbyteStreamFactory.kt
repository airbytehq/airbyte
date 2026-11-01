/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class RedisAirbyteStreamFactory : AirbyteStreamFactory {
    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream,
    ): AirbyteStream {
        val keyType =
            RedisKeyType.entries.firstOrNull { it.streamName == discoveredStream.id.name }
                ?: return AirbyteStreamFactory.createAirbyteStream(discoveredStream)
        val properties = Jsons.objectNode()
        for (field in keyType.fields) {
            properties.set<ObjectNode>(field.name, field.type.schema())
        }
        val schema =
            Jsons.objectNode().put("type", "object").set<ObjectNode>("properties", properties)
        val stream =
            AirbyteStream()
                .withName(keyType.streamName)
                .withJsonSchema(schema)
                .withSupportedSyncModes(
                    if (keyType.incremental) {
                        listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                    } else {
                        listOf(SyncMode.FULL_REFRESH)
                    },
                )
                .withSourceDefinedPrimaryKey(keyType.primaryKey)
                .withIsResumable(true)
        if (keyType.incremental) {
            stream.sourceDefinedCursor = true
            stream.defaultCursorField = listOf("id")
        } else {
            stream.defaultCursorField = null
        }
        return stream
    }

    private fun RedisFieldType.schema(): ObjectNode =
        when (this) {
            RedisFieldType.STRING -> Jsons.objectNode().put("type", "string")
            RedisFieldType.INTEGER ->
                Jsons.objectNode().put("type", "number").put("airbyte_type", "integer")
            RedisFieldType.JSONB ->
                Jsons.objectNode()
                    .put("type", "object")
                    .set<ObjectNode>(
                        "additionalProperties",
                        Jsons.objectNode().put("type", "string"),
                    )
            RedisFieldType.ARRAY_STRING ->
                Jsons.objectNode()
                    .put("type", "array")
                    .set<ObjectNode>("items", Jsons.objectNode().put("type", "string"))
            RedisFieldType.ARRAY_JSONB ->
                Jsons.objectNode()
                    .put("type", "array")
                    .set<ObjectNode>(
                        "items",
                        Jsons.objectNode()
                            .put("type", "object")
                            .set<ObjectNode>(
                                "properties",
                                Jsons.objectNode()
                                    .set<ObjectNode>(
                                        "member",
                                        Jsons.objectNode().put("type", "string"),
                                    )
                                    .set<ObjectNode>(
                                        "score",
                                        Jsons.objectNode().put("type", "number"),
                                    ),
                            ),
                    )
        }
}
