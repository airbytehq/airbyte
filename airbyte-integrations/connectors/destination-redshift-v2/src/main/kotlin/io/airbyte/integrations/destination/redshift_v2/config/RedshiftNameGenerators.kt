/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameGenerator
import io.airbyte.cdk.load.table.FinalTableNameGenerator
import io.airbyte.integrations.destination.redshift_v2.schema.RedshiftTableSchemaMapper
import io.airbyte.integrations.destination.redshift_v2.schema.toRedshiftCompatibleName
import jakarta.inject.Singleton

@Singleton
class RedshiftFinalTableNameGenerator(
    private val mapper: RedshiftTableSchemaMapper,
) : FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        return mapper.toFinalTableName(streamDescriptor)
    }
}

@Singleton
class RedshiftColumnNameGenerator(
    private val mapper: RedshiftTableSchemaMapper,
) : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        val dbName = mapper.toColumnName(column)
        return ColumnNameGenerator.ColumnName(
            displayName = dbName,
            canonicalName = dbName.toRedshiftCompatibleName(),
        )
    }
}
