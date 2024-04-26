/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.ColumnType

/** Union type for columns described within a [StreamKey]. */
sealed interface Column {
    val type: ColumnType
}

data class DataColumn(val metadata: ColumnMetadata, override val type: ColumnType) : Column

data class CursorColumn(
    val name: String,
    override val type: ColumnType,
) : Column
