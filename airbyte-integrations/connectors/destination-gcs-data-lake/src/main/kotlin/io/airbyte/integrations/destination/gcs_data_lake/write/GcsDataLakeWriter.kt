/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import javax.inject.Singleton
import org.apache.iceberg.catalog.TableIdentifier

@Singleton
class GcsDataLakeWriter(
    private val icebergConfiguration: GcsDataLakeConfiguration,
    private val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil,
    private val icebergUtil: IcebergUtil,
    private val icebergTableSynchronizer: IcebergTableSynchronizer,
    private val catalog: DestinationCatalog,
    private val tableIdGenerator: TableIdGenerator,
    private val columnNameMapper: ColumnNameMapper,
    private val streamStateStore: StreamStateStore<GcsDataLakeStreamState>
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
            val incomingTableId =
                tableIdGenerator.toTableIdentifier(incomingStream.mappedDescriptor)
            if (processedTableIds.containsKey(incomingTableId)) {
                val conflictingStream = processedTableIds[incomingTableId]!!
                conflictingStreams.add(
                    Triple(conflictingStream, incomingStream.mappedDescriptor, incomingTableId)
                )
            } else {
                processedTableIds[incomingTableId] = incomingStream.mappedDescriptor
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
        return GcsDataLakeStreamLoader(
            icebergConfiguration,
            stream,
            icebergTableSynchronizer,
            gcsDataLakeCatalogUtil,
            icebergUtil,
            columnNameMapper,
            stagingBranchName =
                io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_STAGING_BRANCH,
            mainBranchName = icebergConfiguration.gcsCatalogConfiguration.mainBranchName,
            streamStateStore = streamStateStore,
        )
    }
}
