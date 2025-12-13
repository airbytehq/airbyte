/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton

@Singleton
class SnowflakeColumnNameMapper(
    private val catalogInfo: TableCatalog,
    private val snowflakeConfiguration: SnowflakeConfiguration,
) : ColumnNameMapper {
    override fun getMappedColumnName(stream: DestinationStream, columnName: String): String {
        if (snowflakeConfiguration.legacyRawTablesOnly == true) {
            return columnName
        } else {
            return catalogInfo.getMappedColumnName(stream, columnName)!!
        }
    }
}
