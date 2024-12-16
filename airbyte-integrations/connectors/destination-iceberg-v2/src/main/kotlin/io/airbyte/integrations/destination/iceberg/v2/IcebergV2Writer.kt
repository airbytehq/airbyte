/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
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
) : DestinationWriter {

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val properties =
            icebergUtil.toCatalogProperties(icebergConfiguration = icebergConfiguration)
        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, properties)
        val pipeline = ParquetMapperPipelineFactory().create(stream)
        val schema = icebergUtil.toIcebergSchema(stream = stream, pipeline = pipeline)
        val table =
            icebergUtil.createTable(
                streamDescriptor = stream.descriptor,
                catalog = catalog,
                schema = schema,
                properties = properties
            )

        existingAndIncomingSchemaShouldBeSame(catalogSchema = schema, tableSchema = table.schema())

        return IcebergStreamLoader(
            stream = stream,
            table = table,
            icebergTableWriterFactory = icebergTableWriterFactory,
            icebergUtil = icebergUtil,
            pipeline = pipeline,
            stagingBranchName = DEFAULT_STAGING_BRANCH,
            mainBranchName = icebergConfiguration.nessieServerConfiguration.mainBranchName,
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
