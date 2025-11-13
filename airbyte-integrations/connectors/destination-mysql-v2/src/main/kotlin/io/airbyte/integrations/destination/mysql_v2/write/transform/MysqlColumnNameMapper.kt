/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

/**
 * MySQL implementation of ColumnNameMapper.
 * Delegates to the TableCatalog to get the mapped column name.
 */
@Singleton
class MysqlColumnNameMapper(private val catalogInfo: TableCatalog) : ColumnNameMapper {
    override fun getMappedColumnName(stream: DestinationStream, columnName: String): String {
        return catalogInfo.getMappedColumnName(stream, columnName)!!
    }
}
