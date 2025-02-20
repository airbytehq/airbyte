/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import javax.inject.Singleton
import org.apache.iceberg.catalog.TableIdentifier

@Singleton
class S3DataLakeWriter(
    private val icebergTableWriterFactory: IcebergTableWriterFactory,
    private val icebergConfiguration: S3DataLakeConfiguration,
    private val s3DataLakeUtil: S3DataLakeUtil,
    private val icebergUtil: IcebergUtil,
    private val icebergTableSynchronizer: IcebergTableSynchronizer,
    private val catalog: DestinationCatalog,
    private val tableIdGenerator: TableIdGenerator,
) : DestinationWriter {
    override suspend fun setup() {
        super.setup()
        val processedTableIds: MutableMap<TableIdentifier, DestinationStream.Descriptor> =
            mutableMapOf()
        val conflictingStreams:
            MutableList<
                Triple<DestinationStream.Descriptor, DestinationStream.Descriptor, TableIdentifier>
            > =
            mutableListOf()
        catalog.streams.forEach { incomingStream ->
            val incomingTableId = tableIdGenerator.toTableIdentifier(incomingStream.descriptor)
            if (processedTableIds.containsKey(incomingTableId)) {
                val conflictingStream = processedTableIds[incomingTableId]!!
                conflictingStreams.add(
                    Triple(conflictingStream, incomingStream.descriptor, incomingTableId)
                )
            } else {
                processedTableIds[incomingTableId] = incomingStream.descriptor
            }
        }
        if (conflictingStreams.isNotEmpty()) {
            throw ConfigErrorException(
                "Detected naming conflicts between streams:\n" +
                    conflictingStreams.joinToString("\n") { (s1, s2, tableId) ->
                        val s1Desc = s1.toPrettyString()
                        val s2Desc = s2.toPrettyString()
                        "$s1Desc - $s2Desc (both writing to $tableId)"
                    }
            )
        }
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return S3DataLakeStreamLoader(
            icebergConfiguration,
            stream,
            icebergTableSynchronizer,
            icebergTableWriterFactory,
            s3DataLakeUtil,
            icebergUtil,
            stagingBranchName = DEFAULT_STAGING_BRANCH,
            mainBranchName = icebergConfiguration.icebergCatalogConfiguration.mainBranchName,
        )
    }
}
