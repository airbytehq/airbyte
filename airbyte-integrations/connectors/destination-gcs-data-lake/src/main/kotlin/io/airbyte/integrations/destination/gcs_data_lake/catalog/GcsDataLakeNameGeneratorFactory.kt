/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.tableIdOf
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import org.apache.iceberg.catalog.TableIdentifier

/**
 * Generates BigLake-compatible column names for GCS Data Lake tables.
 *
 * BigLake external tables have strict naming requirements:
 * - Only alphanumeric characters (a-z, A-Z, 0-9) and underscores (_)
 *
 * This implementation uses [Transformations.toAlphanumericAndUnderscore] to ensure all column names
 * meet these requirements.
 */
@Singleton
class GcsDataLakeColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        val sanitized = Transformations.toAlphanumericAndUnderscore(column)
        return ColumnNameGenerator.ColumnName(
            displayName = sanitized,
            canonicalName = sanitized,
        )
    }
}

/**
 * BigLake table ID generator that sanitizes names. BigLake doesn't support special characters
 * (converts to alphanumeric+underscore)
 */
class BigLakeTableIdGenerator(private val databaseName: String) : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val namespace =
            Transformations.toAlphanumericAndUnderscore(stream.namespace ?: databaseName)
        val name = Transformations.toAlphanumericAndUnderscore(stream.name)
        return tableIdOf(namespace, name)
    }
}

@Factory
class GcsDataLakeNameGeneratorFactory(
    private val gcsDataLakeConfiguration: GcsDataLakeConfiguration
) {
    @Singleton
    fun create(): TableIdGenerator = BigLakeTableIdGenerator(gcsDataLakeConfiguration.namespace)

    /**
     * Provides FinalTableNameGenerator for TableCatalog. GCS Data Lake only has one table per
     * stream (no separate raw/final tables), so this generates the same sanitized name for all
     * tables.
     */
    @Singleton
    fun createFinalTableNameGenerator(): FinalTableNameGenerator =
        FinalTableNameGenerator { stream ->
            val namespace =
                Transformations.toAlphanumericAndUnderscore(
                    stream.namespace ?: gcsDataLakeConfiguration.namespace
                )
            val name = Transformations.toAlphanumericAndUnderscore(stream.name)
            TableName(namespace = namespace, name = name)
        }
}
