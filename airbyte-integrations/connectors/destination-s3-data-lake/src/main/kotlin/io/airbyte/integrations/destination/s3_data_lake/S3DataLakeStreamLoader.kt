/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.iceberg.parquet.IcebergParquetPipelineFactory
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.toolkits.iceberg.parquet.ColumnTypeChangeBehavior
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3DataLakeStreamLoader(
    private val icebergConfiguration: S3DataLakeConfiguration,
    override val stream: DestinationStream,
    private val icebergTableSynchronizer: IcebergTableSynchronizer,
    private val s3DataLakeUtil: S3DataLakeUtil,
    private val icebergUtil: IcebergUtil,
    private val stagingBranchName: String,
    private val mainBranchName: String,
    private val streamStateStore: StreamStateStore<S3DataLakeStreamState>,
) : StreamLoader {
    private lateinit var table: Table
    private lateinit var targetSchema: Schema
    private val pipeline = IcebergParquetPipelineFactory().create(stream)

    // If we're executing a truncate, then force the schema change.
    internal val columnTypeChangeBehavior: ColumnTypeChangeBehavior =
        if (stream.isSingleGenerationTruncate()) {
            ColumnTypeChangeBehavior.OVERWRITE
        } else {
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        }
    private val incomingSchema = icebergUtil.toIcebergSchema(stream = stream, pipeline = pipeline)

    @SuppressFBWarnings(
        "RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE",
        "something about the `table` lateinit var is confusing spotbugs"
    )
    override suspend fun start() {
        val properties = s3DataLakeUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, properties)
        s3DataLakeUtil.createNamespaceWithGlueHandling(stream.descriptor, catalog)
        table =
            icebergUtil.createTable(
                streamDescriptor = stream.descriptor,
                catalog = catalog,
                schema = incomingSchema,
                properties = properties
            )

        // Note that if we have columnTypeChangeBehavior OVERWRITE, we don't commit the schema
        // change immediately. This is intentional.
        // If we commit the schema change right now, then affected columns might become unqueryable.
        // Instead, we write data using the new schema to the staging branch - that data will be
        // unqueryable during the sync (which is fine).
        // Also note that we're not wrapping the entire sync in a transaction
        // (i.e. `table.newTransaction()`).
        // This is also intentional - the airbyte protocol requires that we commit data
        // incrementally, and if the entire sync is in a transaction, we might crash before we can
        // commit that transaction.
        targetSchema = computeOrExecuteSchemaUpdate().schema
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

        val state =
            S3DataLakeStreamState(
                table = table,
                schema = targetSchema,
            )
        streamStateStore.put(stream.descriptor, state)
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            // Doing it first to make sure that data coming in the current batch is written to the
            // main branch
            logger.info {
                "No stream failure detected. Committing changes from staging branch '$stagingBranchName' to main branch '$mainBranchName."
            }
            // We've modified the table over the sync (i.e. adding new snapshots)
            // so we need to refresh here to get the latest table metadata.
            // In principle, this doesn't matter, but the iceberg SDK throws an error about
            // stale table metadata without this.
            table.refresh()
            computeOrExecuteSchemaUpdate().pendingUpdate?.commit()
            table.manageSnapshots().fastForwardBranch(mainBranchName, stagingBranchName).commit()

            if (stream.minimumGenerationId > 0) {
                logger.info {
                    "Detected a minimum generation ID (${stream.minimumGenerationId}). Preparing to delete obsolete generation IDs."
                }
                val generationIdsToDelete =
                    (0 until stream.minimumGenerationId).map(
                        icebergUtil::constructGenerationIdSuffix
                    )
                val icebergTableCleaner = IcebergTableCleaner(icebergUtil = icebergUtil)
                icebergTableCleaner.deleteGenerationId(
                    table,
                    stagingBranchName,
                    generationIdsToDelete
                )
                //  Doing it again to push the deletes from the staging to main branch
                logger.info {
                    "Deleted obsolete generation IDs up to ${stream.minimumGenerationId - 1}. " +
                        "Pushing these updates to the '$mainBranchName' branch."
                }
                table
                    .manageSnapshots()
                    .fastForwardBranch(mainBranchName, stagingBranchName)
                    .commit()
            }
        }
    }

    /**
     * We can't just cache the SchemaUpdateResult from [start], because when we try to `commit()` it
     * in [close], Iceberg throws a stale table metadata exception. So instead we have to calculate
     * it twice - once at the start of the sync, to get the updated table schema, and once again at
     * the end of the sync, to get a fresh [UpdateSchema] instance.
     */
    private fun computeOrExecuteSchemaUpdate() =
        icebergTableSynchronizer.maybeApplySchemaChanges(
            table,
            incomingSchema,
            columnTypeChangeBehavior,
        )
}
