/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.util.Locale

// Unused but needed by another bean
@Singleton
class ClickhouseRawTableNameGenerators(
    private val config: ClickhouseConfiguration,
    private val uuidGenerator: UUIDGenerator
) : RawTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName =
        // The raw table is not implemented by Clickhouse, in order to avoid fake table collision,
        // we are passing a random UUID for the name
        TableName(
            config.resolvedDatabase,
            uuidGenerator.v7().toString(),
        )
}

@Singleton
class ClickhouseFinalTableNameGenerator(private val config: ClickhouseConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName =
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
