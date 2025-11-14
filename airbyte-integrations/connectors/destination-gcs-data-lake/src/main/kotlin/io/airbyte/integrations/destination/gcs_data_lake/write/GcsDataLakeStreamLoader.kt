/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.toolkits.iceberg.parquet.ColumnTypeChangeBehavior
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.types.Types

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class GcsDataLakeStreamLoader(
    private val icebergConfiguration: GcsDataLakeConfiguration,
    override val stream: DestinationStream,
    private val icebergTableSynchronizer: IcebergTableSynchronizer,
    private val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil,
    private val icebergUtil: IcebergUtil,
    private val columnNameMapper: ColumnNameMapper,
    private val stagingBranchName: String,
    private val mainBranchName: String,
    private val streamStateStore: StreamStateStore<GcsDataLakeStreamState>,
) : StreamLoader {
    private lateinit var table: Table
    private lateinit var targetSchema: Schema

    // If we're executing a truncate, then force the schema change.
    internal val columnTypeChangeBehavior: ColumnTypeChangeBehavior =
        if (stream.isSingleGenerationTruncate()) {
            ColumnTypeChangeBehavior.OVERWRITE
        } else {
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        }

    private val incomingSchema = computeIncomingSchema(false)

    private fun computeIncomingSchema(withIdentifierFields: Boolean) =
        icebergUtil.toIcebergSchema(stream = stream).let { schema ->
            // Transform the schema to use mapped column names for BigLake compatibility.
            // BigLake rejects table creation with special characters in column names.
            transformSchemaWithMappedNames(schema, withIdentifierFields)
        }

    /**
     * Transforms an Iceberg schema to use mapped column names. This ensures column names are
     * BigLake-compatible (alphanumeric + underscore only).
     */
    private fun transformSchemaWithMappedNames(
        schema: Schema,
        withIdentifierFields: Boolean
    ): Schema {
        val mappedFields =
            schema.asStruct().fields().map { field ->
                val originalName = field.name()

                // Skip Airbyte metadata columns - they're already valid
                if (Meta.COLUMN_NAMES.contains(originalName)) {
                    return@map field
                }

                val mappedName = columnNameMapper.getMappedColumnName(stream, originalName)

                if (mappedName != originalName) {
                    Types.NestedField.of(
                        field.fieldId(),
                        field.isOptional,
                        mappedName,
                        field.type(),
                        field.doc()
                    )
                } else {
                    field
                }
            }

        // Don't set identifier fields during table creation - BigLake corrupts them.
        // We'll reconcile them after the table is created.
        return Schema(
            mappedFields,
            if (withIdentifierFields) {
                schema.identifierFieldIds()
            } else {
                emptySet()
            },
        )
    }

    @SuppressFBWarnings(
        "RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE",
        "something about the `table` lateinit var is confusing spotbugs"
    )
    override suspend fun start() {
        val properties = gcsDataLakeCatalogUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog =
            icebergUtil.createCatalog(
                io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_CATALOG_NAME,
                properties
            )
        gcsDataLakeCatalogUtil.createNamespace(stream.mappedDescriptor, catalog)
        table =
            icebergUtil.createTable(
                streamDescriptor = stream.mappedDescriptor,
                catalog = catalog,
                schema = incomingSchema,
            )

        // Reconcile identifier fields after BigLake creates the table
        // BigLake reassigns field IDs, so we need to update the schema with the correct field names
        val primaryKeyNames =
            when (val importType = stream.importType) {
                is Dedupe -> {
                    importType.primaryKey.flatten().map { originalName ->
                        if (Meta.COLUMN_NAMES.contains(originalName)) {
                            originalName
                        } else {
                            columnNameMapper.getMappedColumnName(stream, originalName)
                        }
                    }
                }
                else -> emptyList()
            }

        if (primaryKeyNames.isNotEmpty()) {
            logger.info { "Setting identifier fields to primary keys: $primaryKeyNames" }
            // Only set identifier fields if the table was just created.
            // For existing tables with PK changes, let the IcebergTableSynchronizer handle it
            // (it will set identifier fields after schema evolution in
            // computeOrExecuteSchemaUpdate)
            if (table.history().isEmpty() || table.schema().identifierFieldIds().isEmpty()) {
                table.updateSchema().setIdentifierFields(primaryKeyNames).commit()
                // Refresh to get the updated schema with identifier fields
                table.refresh()
            } else {
                logger.info {
                    "Table already has identifier fields. Will let schema synchronizer handle PK changes."
                }
            }
        }

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

        // After schema updates, refresh the table to ensure we have the latest schema with
        // identifier fields.
        // IMPORTANT: In OVERWRITE mode, the schema update is computed but NOT committed yet
        // (it's pending for commit at close time). So we must NOT overwrite targetSchema with
        // table.schema(), which would give us the OLD schema. The writer MUST use the NEW schema.
        if (columnTypeChangeBehavior == ColumnTypeChangeBehavior.SAFE_SUPERTYPE) {
            table.refresh()
            targetSchema = table.schema()
        }

        logger.info {
            "Final target schema has ${targetSchema.identifierFieldIds().size} identifier fields: ${targetSchema.identifierFieldIds()}"
        }

        try {
            logger.info {
                "maybe creating branch $stagingBranchName for stream ${stream.mappedDescriptor}"
            }
            table.manageSnapshots().createBranch(stagingBranchName).commit()
        } catch (e: IllegalArgumentException) {
            logger.info {
                "branch $stagingBranchName already exists for stream ${stream.mappedDescriptor}"
            }
        }

        val state =
            GcsDataLakeStreamState(
                table = table,
                schema = targetSchema,
            )
        streamStateStore.put(stream.mappedDescriptor, state)
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
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
            val schemaUpdateResult = computeOrExecuteSchemaUpdate()
            val pendingUpdates = schemaUpdateResult.pendingUpdates
            if (!pendingUpdates.isEmpty()) {
                logger.info {
                    "Committing schema update for stream ${stream.mappedDescriptor}. " +
                        "Schema has ${schemaUpdateResult.schema.columns().size} columns."
                }
                try {
                    pendingUpdates.forEach { it.commit() }
                } catch (e: Exception) {
                    logger.error(e) {
                        "Failed to commit schema update for stream ${stream.mappedDescriptor}. " +
                            "Existing table schema: ${table.schema().columns().map { it.name() }}. " +
                            "Incoming schema: ${incomingSchema.columns().map { it.name() }}."
                    }
                    throw e
                }
            }
            table.manageSnapshots().replaceBranch(mainBranchName, stagingBranchName).commit()

            if (stream.isSingleGenerationTruncate()) {
                logger.info {
                    "Detected a minimum generation ID (${stream.minimumGenerationId}). Preparing to delete obsolete generation IDs."
                }
                val icebergTableCleaner = IcebergTableCleaner(icebergUtil = icebergUtil)
                icebergTableCleaner.deleteOldGenerationData(table, stagingBranchName, stream)
                //  Doing it again to push the deletes from the staging to main branch
                logger.info {
                    "Deleted obsolete generation IDs up to ${stream.minimumGenerationId - 1}. " +
                        "Pushing these updates to the '$mainBranchName' branch."
                }
                table.manageSnapshots().replaceBranch(mainBranchName, stagingBranchName).commit()
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
            computeIncomingSchema(true),
            columnTypeChangeBehavior,
            // BigLake requires separate commits when replacing a column (delete+add same name).
            // It rejects schema updates that delete and add a column with the same name
            // in a single transaction, even with different field IDs.
            requireSeparateCommitsForColumnReplace = true,
        )
}
