/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import io.airbyte.cdk.load.component.TableSchema

interface DestinationSchemaExporter {
    suspend fun discoverSchema(namespace: String?, name: String): ExportedTableSchema
}

data class ExportedTableSchema(
    val tableSchema: TableSchema,
    val additionalInfo: Map<String, Any?> = emptyMap(),
)
