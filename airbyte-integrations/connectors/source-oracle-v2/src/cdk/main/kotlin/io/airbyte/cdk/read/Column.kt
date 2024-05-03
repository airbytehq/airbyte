/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.discover.AirbyteType
import io.airbyte.cdk.discover.ColumnMetadata

/** Union type for columns described within a [StreamKey]. */
sealed interface Column {
    val id: String
    val airbyteType: AirbyteType
}

data class DataColumn(val metadata: ColumnMetadata, override val airbyteType: AirbyteType) :
    Column {
    override val id: String
        get() = metadata.label
}

data class AirbyteColumn(
    override val id: String,
    override val airbyteType: AirbyteType,
) : Column
