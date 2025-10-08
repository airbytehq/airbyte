/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.command.DestinationStream

/** Used by the CDK to pass the final column name to the aggregate buffer. */
interface ColumnNameMapper {
    fun getMappedColumnName(stream: DestinationStream, columnName: String): String? = columnName
}
