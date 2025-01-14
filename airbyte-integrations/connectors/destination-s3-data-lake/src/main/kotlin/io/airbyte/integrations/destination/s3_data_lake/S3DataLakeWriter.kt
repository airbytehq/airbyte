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
import javax.inject.Singleton
import org.apache.iceberg.Schema

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

        // TODO : See if the identifier fields are allowed to change
        identifierFieldsShouldNotChange(
            incomingSchema = incomingSchema,
            existingSchema = table.schema()
        )

        s3DataLakeTableSynchronizer.applySchemaChanges(table, incomingSchema)

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

    private fun identifierFieldsShouldNotChange(incomingSchema: Schema, existingSchema: Schema) {
        val incomingIdentifierFields = incomingSchema.identifierFieldNames()
        val existingIdentifierFieldNames = existingSchema.identifierFieldNames()

        val identifiersMissingInIncoming = existingIdentifierFieldNames - incomingIdentifierFields
        val identifiersExtraInIncoming = incomingIdentifierFields - existingIdentifierFieldNames

        if (identifiersMissingInIncoming.isNotEmpty() || identifiersExtraInIncoming.isNotEmpty()) {
            val errorMessage = buildString {
                append("Identifier fields are different:\n")
                if (identifiersMissingInIncoming.isNotEmpty()) {
                    append(
                        "Identifier Fields missing in incoming schema: $identifiersMissingInIncoming\n"
                    )
                }
                if (identifiersExtraInIncoming.isNotEmpty()) {
                    append(
                        "Identifier Extra fields in incoming schema: $identifiersExtraInIncoming\n"
                    )
                }
            }
            throw IllegalArgumentException(errorMessage)
        }
    }
}
