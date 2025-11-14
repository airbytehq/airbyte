/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.ImportType

data class StreamTableSchema(
    val tableNames: TableNames,
    val columnSchema: ColumnSchema,
    val importType: ImportType,
)
