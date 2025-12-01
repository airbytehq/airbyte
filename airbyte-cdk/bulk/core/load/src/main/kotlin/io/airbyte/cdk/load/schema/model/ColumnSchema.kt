/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.model

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType

data class ColumnSchema(
    // schema on input catalog
    val inputSchema: Map<String, FieldType>,
    // name on input catalog to final resolved name
    val inputToFinalColumnNames: Map<String, String>,
    // resolved name to resolved type
    val finalColumnSchema: Map<String, ColumnType>,
)
