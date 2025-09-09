package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.command.DestinationStream

interface ColumnNameMapper {
    fun getMappedColumnName(stream: DestinationStream, columnName: String): String? = columnName
}
