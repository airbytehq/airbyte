/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg.parquet.IcebergParquetPipelineFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableWriterFactory
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import javax.inject.Singleton
import org.apache.iceberg.Schema

@Singleton
class IcebergV2Writer(
    private val icebergTableWriterFactory: IcebergTableWriterFactory,
    private val icebergConfiguration: IcebergV2Configuration,
    private val icebergUtil: IcebergUtil,
    private val icebergTableSynchronizer: IcebergTableSynchronizer
) : DestinationWriter {

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val properties = icebergUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, properties)
        val pipeline = IcebergParquetPipelineFactory().create(stream)
        val incomingSchema = icebergUtil.toIcebergSchema(stream = stream, pipeline = pipeline)
        val table =
            icebergUtil.createTable(
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

        icebergTableSynchronizer.applySchemaChanges(table, incomingSchema)

        return IcebergStreamLoader(
            stream = stream,
            table = table,
            icebergTableWriterFactory = icebergTableWriterFactory,
            icebergUtil = icebergUtil,
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
