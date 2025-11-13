/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
class DestinationStreamFactory(
    private val jsonSchemaToAirbyteType: JsonSchemaToAirbyteType,
    private val namespaceMapper: NamespaceMapper,
    private val columnNameResolver: ColumnNameResolver,
) {
    fun make(stream: ConfiguredAirbyteStream): DestinationStream {
        // First convert the schema
        val airbyteSchema = jsonSchemaToAirbyteType.convert(stream.stream.jsonSchema)

        // Create column name mapping with collision handling
        val columnNameMapping =
            columnNameResolver.createColumnNameMapping(
                stream.stream.namespace,
                stream.stream.name,
                airbyteSchema,
            )

        return DestinationStream(
            unmappedNamespace = stream.stream.namespace,
            unmappedName = stream.stream.name,
            namespaceMapper = namespaceMapper,
            importType =
                when (stream.destinationSyncMode) {
                    null -> throw IllegalArgumentException("Destination sync mode was null")
                    DestinationSyncMode.APPEND -> Append
                    DestinationSyncMode.OVERWRITE -> Overwrite
                    DestinationSyncMode.APPEND_DEDUP ->
                        Dedupe(primaryKey = stream.primaryKey, cursor = stream.cursorField)
                    DestinationSyncMode.UPDATE -> Update
                    DestinationSyncMode.SOFT_DELETE -> SoftDelete
                },
            generationId = stream.generationId,
            minimumGenerationId = stream.minimumGenerationId,
            syncId = stream.syncId,
            schema = airbyteSchema,
            isFileBased = stream.stream.isFileBased ?: false,
            includeFiles = stream.includeFiles ?: false,
            destinationObjectName = stream.destinationObjectName,
            matchingKey =
                stream.destinationObjectName?.let {
                    fromCompositeNestedKeyToCompositeKey(stream.primaryKey)
                },
            columnMappings = columnNameMapping,
        )
    }

    private fun fromCompositeNestedKeyToCompositeKey(
        compositeNestedKey: List<List<String>>
    ): List<String> {
        if (compositeNestedKey.any { it.size > 1 }) {
            throw IllegalArgumentException(
                "Nested keys are not supported for matching keys. Key was $compositeNestedKey",
            )
        }
        if (compositeNestedKey.any { it.isEmpty() }) {
            throw IllegalArgumentException(
                "Parts of the composite key need to have at least one element. Key was $compositeNestedKey",
            )
        }

        return compositeNestedKey.map { it[0] }.toList()
    }
}
