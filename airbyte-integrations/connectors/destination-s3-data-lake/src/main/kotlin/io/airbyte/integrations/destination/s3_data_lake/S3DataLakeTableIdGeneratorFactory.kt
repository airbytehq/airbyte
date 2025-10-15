/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.tableIdOf
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.iceberg.catalog.TableIdentifier

/** AWS Glue requires lowercase database+table names. */
class GlueTableIdGenerator(private val databaseName: String?) : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val namespace =
            Transformations.toAlphanumericAndUnderscore(
                (stream.namespace ?: databaseName)!!.lowercase()
            )
        val name = Transformations.toAlphanumericAndUnderscore(stream.name.lowercase())
        return tableIdOf(namespace, name)
    }
}

@Factory
class TableIdGeneratorFactory(private val s3DataLakeConfiguration: S3DataLakeConfiguration) {
    @Singleton
    fun create() =
        when (s3DataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration) {
            is GlueCatalogConfiguration ->
                GlueTableIdGenerator(
                    (s3DataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration
                            as GlueCatalogConfiguration)
                        .databaseName
                )
            is NessieCatalogConfiguration ->
                SimpleTableIdGenerator(
                    (s3DataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration
                            as NessieCatalogConfiguration)
                        .namespace
                )
            is RestCatalogConfiguration ->
                SimpleTableIdGenerator(
                    (s3DataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration
                            as RestCatalogConfiguration)
                        .namespace
                )
        }
}
