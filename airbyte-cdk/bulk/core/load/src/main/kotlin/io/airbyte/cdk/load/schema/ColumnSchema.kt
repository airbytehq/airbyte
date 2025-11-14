/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType

data class ColumnSchema(
    val rawSchema: Map<String, FieldType>,
    // raw schema name to final resolved name
    val rawToFinalColumnNames: Map<String, String>,
    // resolved name to resolved type
    val finalColumnSchema: Map<String, ColumnType>
)
