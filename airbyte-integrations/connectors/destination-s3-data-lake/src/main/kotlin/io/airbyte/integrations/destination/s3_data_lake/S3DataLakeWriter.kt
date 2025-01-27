/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg.parquet.IcebergParquetPipelineFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeTableWriterFactory
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
class S3DataLakeWriter(
    private val s3DataLakeTableWriterFactory: S3DataLakeTableWriterFactory,
    private val icebergConfiguration: S3DataLakeConfiguration,
    private val s3DataLakeUtil: S3DataLakeUtil,
    private val s3DataLakeTableSynchronizer: S3DataLakeTableSynchronizer
) : DestinationWriter {

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val properties = s3DataLakeUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog = s3DataLakeUtil.createCatalog(DEFAULT_CATALOG_NAME, properties)
        val pipeline = IcebergParquetPipelineFactory().create(stream)
        val incomingSchema = s3DataLakeUtil.toIcebergSchema(stream = stream, pipeline = pipeline)
        val table =
            s3DataLakeUtil.createTable(
                streamDescriptor = stream.descriptor,
                catalog = catalog,
                schema = incomingSchema,
                properties = properties
            )

        s3DataLakeTableSynchronizer.applySchemaChanges(table, incomingSchema)

        try {
            logger.info {
                "maybe creating branch $DEFAULT_STAGING_BRANCH for stream ${stream.descriptor}"
            }
            table.manageSnapshots().createBranch(DEFAULT_STAGING_BRANCH).commit()
        } catch (e: IllegalArgumentException) {
            logger.info {
                "branch $DEFAULT_STAGING_BRANCH already exists for stream ${stream.descriptor}"
            }
        }

        return S3DataLakeStreamLoader(
            stream = stream,
            table = table,
            s3DataLakeTableWriterFactory = s3DataLakeTableWriterFactory,
            s3DataLakeUtil = s3DataLakeUtil,
            pipeline = pipeline,
            stagingBranchName = DEFAULT_STAGING_BRANCH,
            mainBranchName = icebergConfiguration.icebergCatalogConfiguration.mainBranchName,
        )
    }
}
