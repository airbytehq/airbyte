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
    private val s3DataLakeUtil: S3DataLakeUtil
) : DestinationWriter {

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val properties = s3DataLakeUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog = s3DataLakeUtil.createCatalog(DEFAULT_CATALOG_NAME, properties)
        val pipeline = IcebergParquetPipelineFactory().create(stream)
        val schema = s3DataLakeUtil.toIcebergSchema(stream = stream, pipeline = pipeline)
        val table =
            s3DataLakeUtil.createTable(
                streamDescriptor = stream.descriptor,
                catalog = catalog,
                schema = schema,
                properties = properties
            )

        existingAndIncomingSchemaShouldBeSame(catalogSchema = schema, tableSchema = table.schema())

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

    private fun existingAndIncomingSchemaShouldBeSame(catalogSchema: Schema, tableSchema: Schema) {
        val incomingFieldSet =
            catalogSchema
                .asStruct()
                .fields()
                .map { Triple(it.name(), it.type().typeId(), it.isOptional) }
                .toSet()
        val existingFieldSet =
            tableSchema
                .asStruct()
                .fields()
                .map { Triple(it.name(), it.type().typeId(), it.isOptional) }
                .toSet()

        val missingInIncoming = existingFieldSet - incomingFieldSet
        val extraInIncoming = incomingFieldSet - existingFieldSet

        if (missingInIncoming.isNotEmpty() || extraInIncoming.isNotEmpty()) {
            val errorMessage = buildString {
                append("Table schema fields are different than catalog schema:\n")
                if (missingInIncoming.isNotEmpty()) {
                    append("Fields missing in incoming schema: $missingInIncoming\n")
                }
                if (extraInIncoming.isNotEmpty()) {
                    append("Extra fields in incoming schema: $extraInIncoming\n")
                }
            }
            throw IllegalArgumentException(errorMessage)
        }

        val incomingIdentifierFields = catalogSchema.identifierFieldNames()
        val existingIdentifierFieldNames = tableSchema.identifierFieldNames()

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
