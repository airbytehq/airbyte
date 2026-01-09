/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.tableIdOf
import org.apache.iceberg.catalog.TableIdentifier

/**
 * BigLake table ID generator that sanitizes names.
 * BigLake doesn't support special characters (converts to alphanumeric+underscore)
 * 
 * NOTE: Name sanitization logic duplicated in GcsDataLakeTableSchemaMapper (different CDK interfaces).
 */
class BigLakeTableIdGenerator(private val databaseName: String) : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val namespace =
            Transformations.toAlphanumericAndUnderscore(stream.namespace ?: databaseName)
        val name = Transformations.toAlphanumericAndUnderscore(stream.name)
        return tableIdOf(namespace, name)
    }
}