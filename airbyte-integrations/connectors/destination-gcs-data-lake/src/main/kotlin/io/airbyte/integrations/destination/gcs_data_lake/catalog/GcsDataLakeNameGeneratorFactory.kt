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
 * - Prefixes with underscore if it starts with a number
 *
 * This implementation uses [Transformations.toAlphanumericAndUnderscore] to ensure all column names
 * meet these requirements.
 */
@Singleton
class GcsDataLakeColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        val sanitized = sanitizeBigLakeName(column)
        return ColumnNameGenerator.ColumnName(
            displayName = sanitized,
            canonicalName = sanitized,
        )
    }
}

/**
 * Sanitizes a name to be BigLake/BigQuery compatible.
 * - Converts to alphanumeric + underscore only
 * - Prefixes with underscore if it starts with a number
 */
private fun sanitizeBigLakeName(name: String): String {
    var sanitized = Transformations.toAlphanumericAndUnderscore(name)
    // BigLake/BigQuery doesn't allow table names starting with numbers
    // Prefix with underscore if it starts with a digit
    if (sanitized.isNotEmpty() && sanitized[0].isDigit()) {
        sanitized = "_$sanitized"
    }
    return sanitized
}

/**
 * BigLake table ID generator that sanitizes names. BigLake doesn't support:
 * - Special characters (converts to alphanumeric+underscore)
 * - Table names starting with numbers (prefixes with underscore)
 */
class BigLakeTableIdGenerator(private val databaseName: String) : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val namespace = sanitizeBigLakeName(stream.namespace ?: databaseName)
        val name = sanitizeBigLakeName(stream.name)
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
                sanitizeBigLakeName(stream.namespace ?: gcsDataLakeConfiguration.namespace)
            val name = sanitizeBigLakeName(stream.name)
            TableName(namespace = namespace, name = name)
        }
}
