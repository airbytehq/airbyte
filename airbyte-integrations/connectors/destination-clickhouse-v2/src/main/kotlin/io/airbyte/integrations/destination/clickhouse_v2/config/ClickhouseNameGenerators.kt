/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.util.Locale

@Singleton
class ClickhouseFinalTableNameGenerator(private val config: ClickhouseConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            namespace = streamDescriptor.namespace ?: config.resolvedDatabase,
            name = streamDescriptor.name,
        )
}

@Singleton
class ClickhouseColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column,
            column.lowercase(Locale.getDefault()),
        )
    }
}
