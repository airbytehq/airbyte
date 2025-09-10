/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import jakarta.inject.Singleton

@Singleton
class SnowflakeColumnNameMapper : ColumnNameMapper {

    override fun getMappedColumnName(stream: DestinationStream, columnName: String) = columnName
}
