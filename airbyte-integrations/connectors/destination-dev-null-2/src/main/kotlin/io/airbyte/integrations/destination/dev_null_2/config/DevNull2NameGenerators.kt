/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import jakarta.inject.Singleton

/**
 * Name generators for dev-null destination. These are required by the CDK's TableCatalog even
 * though we don't actually create tables.
 */
@Singleton
class DevNull2RawTableNameGenerator : RawTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val namespace = streamDescriptor.namespace ?: "default"
        val name = "_airbyte_raw_${streamDescriptor.name}"
        return TableName(namespace, name)
    }
}

@Singleton
class DevNull2FinalTableNameGenerator : FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val namespace = streamDescriptor.namespace ?: "default"
        val name = streamDescriptor.name
        return TableName(namespace, name)
    }
}

@Singleton
class DevNull2ColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        // Identity mapping - keep column names as-is
        return ColumnNameGenerator.ColumnName(
            canonicalName = column,
            displayName = column,
        )
    }
}
