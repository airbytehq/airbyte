/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

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
                                .withJsonSchema(
                                    """{"type": "object", "properties": {"id1": {"type": "integer"}, "id2": {"type": "integer"}, "cursor": {"type": "integer"}}, "additionalProperties": false}""".deserializeToNode()
                                )
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
                                .withJsonSchema(
                                    """{"type": "object", "properties": {"id1": {"type": "integer"}, "id2": {"type": "integer"}, "cursor": {"type": "integer"}}, "additionalProperties": false}""".deserializeToNode()
                                )
                                .withNamespace("namespace4")
                                .withName("name4")
                                .withIsFileBased(true)
                        )
                        .withPrimaryKey(listOf(listOf("id1"), listOf("id2")))
                        .withCursorField(listOf("cursor")),
                ),
            )

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
                namespaceMapper = NamespaceMapper(),
                tableSchema =
                    StreamTableSchema(
                        tableNames = TableNames(finalTableName = TableName("namespace", "name")),
                        columnSchema =
                            ColumnSchema(
                                inputSchema =
                                    linkedMapOf(
                                        "z" to FieldType(StringType, nullable = true),
                                        "y" to FieldType(BooleanType, nullable = true),
                                        "x" to FieldType(IntegerType, nullable = true),
                                    ),
                                inputToFinalColumnNames = mapOf("z" to "z", "y" to "y", "x" to "x"),
                                finalSchema = mapOf(),
                            ),
                        importType = Append,
                    )
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

    @Test
    fun throwOnDuplicateStreams() {
        val e =
            assertThrows<ConfigErrorException> {
                DestinationCatalog(
                    listOf(
                        DestinationStream(
                            unmappedNamespace = null,
                            unmappedName = "foo",
                            importType = Append,
                            generationId = 1,
                            minimumGenerationId = 0,
                            syncId = 1,
                            includeFiles = false,
                            schema = ObjectType(linkedMapOf()),
                            namespaceMapper = NamespaceMapper(),
                            tableSchema =
                                StreamTableSchema(
                                    tableNames =
                                        TableNames(finalTableName = TableName("default", "foo")),
                                    columnSchema =
                                        ColumnSchema(
                                            inputSchema = mapOf(),
                                            inputToFinalColumnNames = mapOf(),
                                            finalSchema = mapOf(),
                                        ),
                                    importType = Append,
                                )
                        ),
                        DestinationStream(
                            unmappedNamespace = null,
                            unmappedName = "foo",
                            importType = Append,
                            generationId = 1,
                            minimumGenerationId = 0,
                            syncId = 1,
                            includeFiles = false,
                            schema = ObjectType(linkedMapOf()),
                            namespaceMapper = NamespaceMapper(),
                            tableSchema =
                                StreamTableSchema(
                                    tableNames =
                                        TableNames(finalTableName = TableName("default", "foo")),
                                    columnSchema =
                                        ColumnSchema(
                                            inputSchema = mapOf(),
                                            inputToFinalColumnNames = mapOf(),
                                            finalSchema = mapOf(),
                                        ),
                                    importType = Append,
                                )
                        ),
                    )
                )
            }
        assertEquals("Some streams appeared multiple times: [foo]", e.message)
    }

    @Test
    fun validatePkExists() {
        val e =
            assertThrows<ConfigErrorException> {
                DestinationCatalog(
                    listOf(
                        DestinationStream(
                            unmappedNamespace = null,
                            unmappedName = "foo",
                            importType =
                                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                            generationId = 1,
                            minimumGenerationId = 0,
                            syncId = 1,
                            includeFiles = false,
                            schema = ObjectType(linkedMapOf()),
                            namespaceMapper = NamespaceMapper(),
                            tableSchema =
                                StreamTableSchema(
                                    tableNames =
                                        TableNames(finalTableName = TableName("default", "foo")),
                                    columnSchema =
                                        ColumnSchema(
                                            inputSchema = mapOf(),
                                            inputToFinalColumnNames = mapOf(),
                                            finalSchema = mapOf(),
                                        ),
                                    importType =
                                        Dedupe(
                                            primaryKey = listOf(listOf("id")),
                                            cursor = emptyList()
                                        ),
                                )
                        )
                    )
                )
            }
        assertEquals(
            "For stream foo: A primary key column does not exist in the schema: id",
            e.message
        )
    }

    @Test
    fun validateCursorExists() {
        val e =
            assertThrows<ConfigErrorException> {
                DestinationCatalog(
                    listOf(
                        DestinationStream(
                            unmappedNamespace = null,
                            unmappedName = "foo",
                            importType =
                                Dedupe(
                                    primaryKey = listOf(listOf("id")),
                                    cursor = listOf("updated_at"),
                                ),
                            generationId = 1,
                            minimumGenerationId = 0,
                            syncId = 1,
                            includeFiles = false,
                            schema =
                                ObjectType(
                                    linkedMapOf("id" to FieldType(IntegerType, nullable = true))
                                ),
                            namespaceMapper = NamespaceMapper(),
                            tableSchema =
                                StreamTableSchema(
                                    tableNames =
                                        TableNames(finalTableName = TableName("default", "foo")),
                                    columnSchema =
                                        ColumnSchema(
                                            inputSchema =
                                                linkedMapOf(
                                                    "id" to FieldType(IntegerType, nullable = true)
                                                ),
                                            inputToFinalColumnNames = mapOf("id" to "id"),
                                            finalSchema = mapOf(),
                                        ),
                                    importType =
                                        Dedupe(
                                            primaryKey = listOf(listOf("id")),
                                            cursor = listOf("updated_at"),
                                        ),
                                )
                        )
                    )
                )
            }
        assertEquals(
            "For stream foo: The cursor does not exist in the schema: updated_at",
            e.message
        )
    }
}
