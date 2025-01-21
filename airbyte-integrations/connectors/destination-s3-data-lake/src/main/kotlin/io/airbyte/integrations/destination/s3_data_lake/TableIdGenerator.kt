/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier

/**
 * Convert our internal stream descriptor to an Iceberg [TableIdentifier]. Implementations should
 * handle catalog-specific naming restrictions.
 */
// TODO accept default namespace in config as a val here
interface TableIdGenerator {
    fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier
}

class SimpleTableIdGenerator(private val s3DataLakeConfiguration: S3DataLakeConfiguration) :
    TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val namespace =
            stream.namespace ?: s3DataLakeConfiguration.icebergCatalogConfiguration.databaseName
        return tableIdOf(namespace!!, stream.name)
    }
}

/** AWS Glue requires lowercase database+table names. */
class GlueTableIdGenerator(private val s3DataLakeConfiguration: S3DataLakeConfiguration) :
    TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val fallbackNamespace = s3DataLakeConfiguration.icebergCatalogConfiguration.databaseName
        val namespace = (stream.namespace ?: fallbackNamespace)?.lowercase()

        return tableIdOf(namespace!!, stream.name.lowercase())
    }
}

@Factory
class TableIdGeneratorFactory(private val s3DataLakeConfiguration: S3DataLakeConfiguration) {
    @Singleton
    fun create() =
        when (s3DataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration) {
            is GlueCatalogConfiguration -> GlueTableIdGenerator(s3DataLakeConfiguration)
            else -> SimpleTableIdGenerator(s3DataLakeConfiguration)
        }
}

// iceberg namespace+name must both be nonnull.
private fun tableIdOf(namespace: String, name: String) =
    TableIdentifier.of(Namespace.of(namespace), name)
