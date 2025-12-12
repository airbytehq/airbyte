/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.model

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType

/** Defines column mappings and types from source input to destination table schema. */
data class ColumnSchema(
    // schema on input catalog
    val inputSchema: Map<String, FieldType>,
    // column name on input catalog to resolved name
    val inputToFinalColumnNames: Map<String, String>,
    // resolved name to resolved type
    val finalSchema: Map<String, ColumnType>,
)
