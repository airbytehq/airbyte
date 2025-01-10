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

class SimpleTableIdGenerator : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier =
        tableIdOf(stream.namespace!!, stream.name)
}

/** AWS Glue requires lowercase database+table names. */
class GlueTableIdGenerator : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier =
        tableIdOf(stream.namespace!!.lowercase(), stream.name.lowercase())
}

@Factory
class TableIdGeneratorFactory(private val icebergConfiguration: S3DataLakeConfiguration) {
    @Singleton
    fun create() =
        when (icebergConfiguration.icebergCatalogConfiguration.catalogConfiguration) {
            is GlueCatalogConfiguration -> GlueTableIdGenerator()
            else -> SimpleTableIdGenerator()
        }
}

// iceberg namespace+name must both be nonnull.
private fun tableIdOf(namespace: String, name: String) =
    TableIdentifier.of(Namespace.of(namespace), name)
