/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.nessie.NessieCatalog

@Singleton
class IcebergV2Writer(
    private val icebergConfiguration: IcebergV2Configuration,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
) : DestinationWriter {

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        //        val nessieCatalog = nessieCatalog(icebergConfiguration)
        //        val pipeline = ParquetMapperPipelineFactory().create(stream)
        //         val catalogSchema =
        //            pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema()
        //        val of =
        //            TableIdentifier.of(Namespace.of(stream.descriptor.namespace),
        // stream.descriptor.name)
        //
        //        val table = table(nessieCatalog, of, catalogSchema, PartitionSpec.unpartitioned())
        //
        //
        //        return IcebergStreamLoader(stream, table, ,"a",
        // icebergConfiguration.nessieServerConfiguration.mainBranchName, )
        TODO()
    }

    private fun nessieCatalog(icebergConfiguration: IcebergV2Configuration): NessieCatalog {
        val catalogProperties: MutableMap<String, String> = java.util.HashMap()

        catalogProperties[CatalogProperties.URI] =
            icebergConfiguration.nessieServerConfiguration.serverUri
        catalogProperties["nessie.ref"] = "main"
        if (icebergConfiguration.nessieServerConfiguration.accessToken != null) {
            catalogProperties["nessie.authentication.type"] = "BEARER"
            catalogProperties["nessie.authentication.token"] =
                icebergConfiguration.nessieServerConfiguration.accessToken!!
        }

        catalogProperties[CatalogProperties.WAREHOUSE_LOCATION] =
            icebergConfiguration.nessieServerConfiguration.warehouseLocation

        // Use Iceberg's S3FileIO for file operations
        catalogProperties[CatalogProperties.FILE_IO_IMPL] = "org.apache.iceberg.aws.s3.S3FileIO"

        // AWS (MinIO) credentials and endpoint configuration
        catalogProperties["s3.access-key-id"] =
            icebergConfiguration.awsAccessKeyConfiguration.accessKeyId!!
        catalogProperties["s3.secret-access-key"] =
            icebergConfiguration.awsAccessKeyConfiguration.secretAccessKey!!
        catalogProperties["s3.region"] =
            icebergConfiguration.s3BucketConfiguration.s3BucketRegion.toString()
        catalogProperties["s3.endpoint"] = icebergConfiguration.s3BucketConfiguration.s3Endpoint!!
        catalogProperties["s3.path-style-access"] = "true" // Required for MinIO

        val catalog = NessieCatalog()

        catalog.setConf(Configuration()) // Required for S3FileIO
        catalog.initialize("nessie", catalogProperties)
        return catalog
    }

    private fun table(
        catalog: NessieCatalog,
        tableIdentifier: TableIdentifier,
        schema: Schema,
        spec: PartitionSpec?
    ): Table {
        if (!catalog.tableExists(tableIdentifier)) {
            if (!catalog.namespaceExists(tableIdentifier.namespace())) {
                catalog.createNamespace(tableIdentifier.namespace())
            }
            return catalog.createTable(tableIdentifier, schema, spec)
        } else {
            return catalog.loadTable(tableIdentifier)
        }
    }
}
