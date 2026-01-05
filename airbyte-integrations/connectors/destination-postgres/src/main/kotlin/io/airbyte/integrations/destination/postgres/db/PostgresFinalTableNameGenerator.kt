/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameGenerator
import io.airbyte.cdk.load.table.FinalTableNameGenerator
import io.airbyte.cdk.load.table.TypingDedupingUtil
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import jakarta.inject.Singleton
import java.util.Locale

@Singleton
class PostgresFinalTableNameGenerator(private val config: PostgresConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val namespace = streamDescriptor.namespace ?: config.schema
        return if (!config.legacyRawTablesOnly) {
            TableName(
                namespace = namespace.toPostgresCompatibleName(),
                name = streamDescriptor.name.toPostgresCompatibleName(),
            )
        } else {
            TableName(
                namespace = config.internalTableSchema!!.lowercase().toPostgresCompatibleName(),
                name =
                    TypingDedupingUtil.concatenateRawTableName(
                            namespace = namespace,
                            name = streamDescriptor.name,
                        )
                        .lowercase()
                        .toPostgresCompatibleName(),
            )
        }
    }
}

@Singleton
class PostgresColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toPostgresCompatibleName(),
            column.lowercase(Locale.getDefault()).toPostgresCompatibleName(),
        )
    }
}
