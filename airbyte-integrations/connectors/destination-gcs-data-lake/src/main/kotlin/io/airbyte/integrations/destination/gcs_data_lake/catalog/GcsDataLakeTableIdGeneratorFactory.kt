/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.tableIdOf
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.iceberg.catalog.TableIdentifier

/**
 * BigLake table ID generator that sanitizes names.
 * BigLake doesn't support:
 * - Special characters (converts to alphanumeric+underscore)
 * - Table names starting with numbers (prefixes with underscore)
 */
class BigLakeTableIdGenerator(private val databaseName: String) : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val namespace = sanitizeName(stream.namespace ?: databaseName)
        val name = sanitizeName(stream.name)
        return tableIdOf(namespace, name)
    }

    private fun sanitizeName(name: String): String {
        var sanitized = Transformations.toAlphanumericAndUnderscore(name)
        // BigLake/BigQuery doesn't allow table names starting with numbers
        // Prefix with underscore if it starts with a digit
        if (sanitized.isNotEmpty() && sanitized[0].isDigit()) {
            sanitized = "_$sanitized"
        }
        return sanitized
    }
}

@Factory
class GcsDataLakeTableIdGeneratorFactory(private val gcsDataLakeConfiguration: GcsDataLakeConfiguration) {
    @Singleton
    fun create(): TableIdGenerator =
        BigLakeTableIdGenerator(gcsDataLakeConfiguration.databaseName)
}
