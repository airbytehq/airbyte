/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class DestinationCatalogTest {
    private val originalCatalog =
        ConfiguredAirbyteCatalog()
            .withStreams(
                listOf(
                    ConfiguredAirbyteStream()
                        .withSyncId(12)
                        .withMinimumGenerationId(34)
                        .withGenerationId(56)
                        .withDestinationSyncMode(DestinationSyncMode.APPEND)
                        .withIncludeFiles(false)
                        .withStream(
                            AirbyteStream()
                                .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                .withNamespace("namespace1")
                                .withName("name1")
                                .withIsFileBased(false)
                        ),
                    ConfiguredAirbyteStream()
                        .withSyncId(12)
                        .withMinimumGenerationId(34)
                        .withGenerationId(56)
                        .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                        .withIncludeFiles(true)
                        .withStream(
                            AirbyteStream()
                                .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                .withNamespace("namespace2")
                                .withName("name2")
                                .withIsFileBased(true)
                        )
                        .withPrimaryKey(listOf(listOf("id1"), listOf("id2")))
                        .withCursorField(listOf("cursor")),
                    ConfiguredAirbyteStream()
                        .withSyncId(12)
                        .withMinimumGenerationId(34)
                        .withGenerationId(56)
                        .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                        .withIncludeFiles(false)
                        .withStream(
                            AirbyteStream()
                                .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                .withNamespace("namespace3")
                                .withName("name3")
                                .withIsFileBased(false)
                        ),
                    ConfiguredAirbyteStream()
                        .withSyncId(12)
                        .withMinimumGenerationId(34)
                        .withGenerationId(56)
                        .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                        .withIncludeFiles(false)
                        .withStream(
                            AirbyteStream()
                                .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                .withNamespace("namespace4")
                                .withName("name4")
                                .withIsFileBased(true)
                        )
                        .withPrimaryKey(listOf(listOf("id1"), listOf("id2")))
                        .withCursorField(listOf("cursor")),
                ),
            )

    @Test
    fun roundTrip() {
        val streamFactory =
            DestinationStreamFactory(
                JsonSchemaToAirbyteType(JsonSchemaToAirbyteType.UnionBehavior.DEFAULT),
                namespaceMapper = NamespaceMapper()
            )
        val catalogFactory = DefaultDestinationCatalogFactory()
        val destinationCatalog =
            catalogFactory.getDestinationCatalog(
                originalCatalog,
                streamFactory,
                operation = "write",
                checkNamespace = null,
                namespaceMapper = NamespaceMapper()
            )
        assertEquals(originalCatalog, destinationCatalog.asProtocolObject())
    }

    @Test
    fun proxyOrderedSchema() {
        val stream =
            DestinationStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                importType = Append,
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                includeFiles = false,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "z" to FieldType(StringType, nullable = true),
                                "y" to FieldType(BooleanType, nullable = true),
                                "x" to FieldType(IntegerType, nullable = true),
                            )
                    ),
                namespaceMapper = NamespaceMapper()
            )
        val expectedOrderedSchema =
            arrayOf(
                FieldAccessor(0, "x", IntegerType),
                FieldAccessor(1, "y", BooleanType),
                FieldAccessor(2, "z", StringType),
            )
        assertEquals(
            expectedOrderedSchema.toList(),
            stream.airbyteValueProxyFieldAccessors.toList()
        )
    }
}
