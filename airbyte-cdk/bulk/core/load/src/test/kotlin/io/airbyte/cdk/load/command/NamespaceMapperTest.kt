/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class NamespaceMapperTest {
    private fun makeStream(
        unmappedNamespace: String,
        unmappedName: String,
        namespaceMapper: NamespaceMapper
    ): DestinationStream {
        return DestinationStream(
            unmappedNamespace = unmappedNamespace,
            unmappedName = unmappedName,
            importType = Append,
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
            schema = ObjectType(linkedMapOf()),
            namespaceMapper = namespaceMapper,
            tableSchema =
                StreamTableSchema(
                    tableNames =
                        TableNames(finalTableName = TableName(unmappedNamespace, unmappedName)),
                    columnSchema =
                        ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = Append,
                )
        )
    }

    @Test
    fun `default mapper does not map`() {
        val mapper = NamespaceMapper()
        val stream =
            makeStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper = mapper,
            )
        Assertions.assertEquals(
            DestinationStream.Descriptor("namespace", "name"),
            stream.mappedDescriptor
        )
    }

    @Test
    fun `prefixes are applied unconditionally`() {
        val mapper = NamespaceMapper(streamPrefix = "prefix_")
        val stream =
            makeStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper = mapper,
            )
        Assertions.assertEquals(
            DestinationStream.Descriptor("namespace", "prefix_name"),
            stream.mappedDescriptor
        )
    }

    @Test
    fun `custom format is not applied not in custom mode`() {
        val mapper =
            NamespaceMapper(
                namespaceDefinitionType = NamespaceDefinitionType.SOURCE,
                namespaceFormat = "custom_format_\${SOURCE_NAMESPACE}",
            )
        val stream =
            makeStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper = mapper
            )
        Assertions.assertEquals(
            DestinationStream.Descriptor("namespace", "name"),
            stream.mappedDescriptor
        )
    }

    @Test
    fun `custom format is applied in custom mode`() {
        val mapper =
            NamespaceMapper(
                namespaceDefinitionType = NamespaceDefinitionType.CUSTOM_FORMAT,
                namespaceFormat = "custom_format_\${SOURCE_NAMESPACE}",
            )
        val stream =
            makeStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper = mapper,
            )
        Assertions.assertEquals(
            DestinationStream.Descriptor("custom_format_namespace", "name"),
            stream.mappedDescriptor
        )
    }

    @Test
    fun `namespace is always null in destination mode`() {
        val mapper =
            NamespaceMapper(
                namespaceDefinitionType = NamespaceDefinitionType.DESTINATION,
            )
        val stream =
            makeStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper = mapper,
            )
        Assertions.assertEquals(DestinationStream.Descriptor(null, "name"), stream.mappedDescriptor)
    }

    @Test
    fun `names are still prefixed in destination mode`() {
        val mapper =
            NamespaceMapper(
                namespaceDefinitionType = NamespaceDefinitionType.DESTINATION,
                streamPrefix = "prefix_",
            )
        val stream =
            makeStream(
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper = mapper,
            )
        Assertions.assertEquals(
            DestinationStream.Descriptor(null, "prefix_name"),
            stream.mappedDescriptor
        )
    }
}
