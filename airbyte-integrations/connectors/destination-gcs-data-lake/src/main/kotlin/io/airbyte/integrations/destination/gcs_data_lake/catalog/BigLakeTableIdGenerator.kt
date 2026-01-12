/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.tableIdOf
import io.airbyte.integrations.destination.gcs_data_lake.schema.GcsDataLakeTableSchemaMapper
import jakarta.inject.Singleton
import org.apache.iceberg.catalog.TableIdentifier

/**
 * Adapts GcsDataLakeTableSchemaMapper to the Iceberg TableIdGenerator interface. Reuses the schema
 * mapper's sanitization logic to ensure consistent naming.
 */
@Singleton
class BigLakeTableIdGenerator(private val schemaMapper: GcsDataLakeTableSchemaMapper) :
    TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val tableName = schemaMapper.toFinalTableName(stream)
        return tableIdOf(tableName.namespace, tableName.name)
    }
}
