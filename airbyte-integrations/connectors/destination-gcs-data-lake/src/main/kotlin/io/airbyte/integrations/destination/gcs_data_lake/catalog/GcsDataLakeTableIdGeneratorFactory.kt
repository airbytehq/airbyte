/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.tableIdOf
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.iceberg.catalog.TableIdentifier

/**
 * Sanitizes a name to be BigLake/BigQuery compatible.
 * - Converts to alphanumeric + underscore only
 * - Prefixes with underscore if it starts with a number
 */
private fun sanitizeBigLakeTableName(name: String): String {
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
        val namespace = sanitizeBigLakeTableName(stream.namespace ?: databaseName)
        val name = sanitizeBigLakeTableName(stream.name)
        return tableIdOf(namespace, name)
    }
}

@Factory
class GcsDataLakeTableIdGeneratorFactory(
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
                sanitizeBigLakeTableName(stream.namespace ?: gcsDataLakeConfiguration.namespace)
            val name = sanitizeBigLakeTableName(stream.name)
            TableName(namespace = namespace, name = name)
        }
}
