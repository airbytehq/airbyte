/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.toolkits.iceberg.parquet.ColumnTypeChangeBehavior
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergDeleteMode
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableUpgrader
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.PositionalDeleteResolutionState
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.enableIdentifierBloomFilters
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.tableFormatVersion
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.AllowNonReversibleUpgrades
import io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_STAGING_BRANCH
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.IcebergDeleteFileType
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.types.Types

private val logger = KotlinLogging.logger {}

class GcsDataLakeStreamLoader(
    private val icebergConfiguration: GcsDataLakeConfiguration,
    override val stream: DestinationStream,
    private val icebergTableSynchronizer: IcebergTableSynchronizer,
    private val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil,
    private val icebergUtil: IcebergUtil,
    private val tableIdGenerator: TableIdGenerator,
    private val stagingBranchName: String,
    private val mainBranchName: String,
    private val streamStateStore: StreamStateStore<GcsDataLakeStreamState>,
) : StreamLoader {
    private lateinit var table: Table
    private lateinit var targetSchema: Schema
    private var stagingBranchCreated = false

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
            transformSchemaWithMappedNames(
                schema,
                stream.tableSchema.columnSchema.inputToFinalColumnNames,
                withIdentifierFields,
            )
        }

    @SuppressFBWarnings(
        "RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE",
        "something about the `table` lateinit var is confusing spotbugs",
    )
    override suspend fun start() {
        val properties = gcsDataLakeCatalogUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog =
            icebergUtil.createCatalog(
                io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_CATALOG_NAME,
                properties,
            )
        gcsDataLakeCatalogUtil.createNamespace(stream.mappedDescriptor, catalog)
        val targetFormatVersion = icebergConfiguration.tableFormatVersion.formatVersion
        val tableExisted =
            catalog.tableExists(tableIdGenerator.toTableIdentifier(stream.mappedDescriptor))
        val createdTable =
            icebergUtil.createTable(
                streamDescriptor = stream.mappedDescriptor,
                catalog = catalog,
                schema = incomingSchema,
                formatVersion = targetFormatVersion,
            )
        table = createdTable
        val actualVersion = tableFormatVersion(createdTable)
        val plannedVersion =
            if (
                tableExisted &&
                    actualVersion == 2 &&
                    targetFormatVersion == 3 &&
                    icebergConfiguration.allowNonReversibleUpgrades != AllowNonReversibleUpgrades.NO
            ) {
                3
            } else if (tableExisted) {
                actualVersion
            } else {
                targetFormatVersion
            }
        val deleteMode = resolveDeleteMode(createdTable, plannedVersion)
        val effectiveFormatVersion =
            reconcileFormatVersion(
                table = createdTable,
                tableExisted = tableExisted,
                targetFormatVersion = targetFormatVersion,
                catalog = catalog,
            )
        check(effectiveFormatVersion == plannedVersion) {
            "Planned format v$plannedVersion but reconciliation produced " +
                "v$effectiveFormatVersion for ${createdTable.name()}."
        }

        // Reconcile identifier fields after BigLake creates the table
        // BigLake reassigns field IDs, so we need to update the schema with the correct field names
        val primaryKeyNames =
            when (val importType = stream.tableSchema.importType) {
                is Dedupe -> {
                    importType.primaryKey.flatten().map { originalName ->
                        if (Meta.COLUMN_NAMES.contains(originalName)) {
                            originalName
                        } else {
                            stream.tableSchema.columnSchema.inputToFinalColumnNames[originalName]
                                ?: originalName
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
            if (
                createdTable.history().isEmpty() ||
                    createdTable.schema().identifierFieldIds().isEmpty()
            ) {
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
            val refs = createdTable.refs()
            val legacyStagingRef = refs[DEFAULT_STAGING_BRANCH]
            val mainBranchRef = refs[mainBranchName]
            if (stagingBranchName in refs) {
                logger.info {
                    "branch $stagingBranchName already exists for stream ${stream.mappedDescriptor}"
                }
            } else if (legacyStagingRef != null) {
                logger.info {
                    "Seeding staging branch $stagingBranchName from legacy branch " +
                        "$DEFAULT_STAGING_BRANCH for stream ${stream.mappedDescriptor}"
                }
                createdTable
                    .manageSnapshots()
                    .createBranch(stagingBranchName, legacyStagingRef.snapshotId())
                    .commit()
            } else if (mainBranchRef == null) {
                createdTable.manageSnapshots().createBranch(stagingBranchName).commit()
            } else {
                logger.info {
                    "Seeding staging branch $stagingBranchName from configured main branch " +
                        "$mainBranchName for stream ${stream.mappedDescriptor}"
                }
                createdTable
                    .manageSnapshots()
                    .createBranch(stagingBranchName, mainBranchRef.snapshotId())
                    .commit()
            }
        } catch (e: IllegalArgumentException) {
            logger.info {
                "branch $stagingBranchName already exists for stream ${stream.mappedDescriptor}"
            }
        }
        stagingBranchCreated = true

        val resolvedDeletesEnabled =
            stream.tableSchema.importType is Dedupe && deleteMode != IcebergDeleteMode.EQUALITY
        val positionalDeleteState =
            if (resolvedDeletesEnabled) {
                enableIdentifierBloomFilters(
                    createdTable,
                    targetSchema,
                    targetSchema.identifierFieldIds(),
                )
                PositionalDeleteResolutionState()
            } else {
                null
            }

        val state =
            GcsDataLakeStreamState(
                table = createdTable,
                schema = targetSchema,
                stagingBranchName = stagingBranchName,
                positionalDeleteState = positionalDeleteState,
                optimizePriorIcebergDeleteFiles =
                    icebergConfiguration.optimizePriorIcebergDeleteFiles,
                deleteMode = deleteMode,
            )
        streamStateStore.put(stream.mappedDescriptor, state)
    }

    private fun reconcileFormatVersion(
        table: Table,
        tableExisted: Boolean,
        targetFormatVersion: Int,
        catalog: Catalog,
    ): Int {
        var effectiveVersion = tableFormatVersion(table)
        if (tableExisted && effectiveVersion != targetFormatVersion) {
            if (effectiveVersion == 2 && targetFormatVersion == 3) {
                when (icebergConfiguration.allowNonReversibleUpgrades) {
                    AllowNonReversibleUpgrades.NO -> {
                        logger.warn {
                            "Table ${table.name()} exists at Iceberg format v2 while " +
                                "table_format_version targets v3. Leaving the table at v2; " +
                                "set allow_non_reversible_upgrades to upgrade it in place " +
                                "(one-way)."
                        }
                    }
                    AllowNonReversibleUpgrades.YES,
                    AllowNonReversibleUpgrades.WITH_TABLE_BACKUP -> {
                        val backup =
                            icebergConfiguration.allowNonReversibleUpgrades ==
                                AllowNonReversibleUpgrades.WITH_TABLE_BACKUP
                        IcebergTableUpgrader.upgradeToV3(
                            catalog,
                            tableIdGenerator.toTableIdentifier(stream.mappedDescriptor),
                            backup = backup,
                        )
                        table.refresh()
                        effectiveVersion = 3
                    }
                }
            } else {
                logger.warn {
                    "Table ${table.name()} exists at Iceberg format v$effectiveVersion while " +
                        "table_format_version targets v$targetFormatVersion. Format versions " +
                        "cannot be lowered; the table stays at v$effectiveVersion."
                }
            }
        }
        return effectiveVersion
    }

    private fun resolveDeleteMode(table: Table, effectiveVersion: Int): IcebergDeleteMode {
        if (stream.tableSchema.importType !is Dedupe) {
            return IcebergDeleteMode.EQUALITY
        }
        return when (icebergConfiguration.icebergDeleteFileType) {
            IcebergDeleteFileType.AUTOMATIC ->
                if (effectiveVersion >= 3) IcebergDeleteMode.DELETION_VECTOR
                else IcebergDeleteMode.EQUALITY
            IcebergDeleteFileType.EQUALITY -> {
                if (effectiveVersion >= 3) {
                    throw ConfigErrorException(
                        "iceberg_delete_file_type EQUALITY requires an Iceberg format v2 " +
                            "table, but ${table.name()} is at format v$effectiveVersion.",
                    )
                }
                IcebergDeleteMode.EQUALITY
            }
            IcebergDeleteFileType.POSITIONAL -> {
                if (effectiveVersion >= 3) {
                    throw ConfigErrorException(
                        "iceberg_delete_file_type POSITIONAL requires an Iceberg format v2 " +
                            "table, but ${table.name()} is at format v$effectiveVersion.",
                    )
                }
                IcebergDeleteMode.POSITIONAL
            }
            IcebergDeleteFileType.DELETION_VECTOR -> {
                if (effectiveVersion < 3) {
                    throw ConfigErrorException(
                        "iceberg_delete_file_type DELETION_VECTOR requires an Iceberg format v3 " +
                            "table, but ${table.name()} is at format v$effectiveVersion and " +
                            "allow_non_reversible_upgrades did not upgrade it.",
                    )
                }
                IcebergDeleteMode.DELETION_VECTOR
            }
        }
    }

    override suspend fun teardown(completedSuccessfully: Boolean) {
        if (!completedSuccessfully) {
            logger.info {
                "Stream ${stream.mappedDescriptor} did not complete successfully. " +
                    "Keeping staging branch $stagingBranchName for recovery."
            }
            return
        }

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

        removeStagingBranch()
        removeLegacyStagingBranch()
    }

    private fun removeStagingBranch() {
        if (!this::table.isInitialized || !stagingBranchCreated) {
            return
        }
        try {
            logger.info {
                "Removing staging branch $stagingBranchName for stream ${stream.mappedDescriptor}"
            }
            table.manageSnapshots().removeBranch(stagingBranchName).commit()
            stagingBranchCreated = false
        } catch (e: Exception) {
            logger.warn(e) {
                "Failed to remove staging branch $stagingBranchName for stream ${stream.mappedDescriptor}"
            }
        }
    }

    private fun removeLegacyStagingBranch() {
        if (!this::table.isInitialized || mainBranchName == DEFAULT_STAGING_BRANCH) {
            return
        }
        if (table.refs()[DEFAULT_STAGING_BRANCH] == null) {
            return
        }
        try {
            logger.info {
                "Removing legacy staging branch $DEFAULT_STAGING_BRANCH for stream ${stream.mappedDescriptor}"
            }
            table.manageSnapshots().removeBranch(DEFAULT_STAGING_BRANCH).commit()
        } catch (e: Exception) {
            logger.warn(e) {
                "Failed to remove legacy staging branch $DEFAULT_STAGING_BRANCH for stream ${stream.mappedDescriptor}"
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

/**
 * Transforms an Iceberg schema to use mapped column names. This ensures column names are
 * BigLake-compatible (alphanumeric + underscore only).
 */
internal fun transformSchemaWithMappedNames(
    schema: Schema,
    inputToFinalColumnNames: Map<String, String>,
    withIdentifierFields: Boolean,
): Schema {
    val mappedFields =
        schema.asStruct().fields().map { field ->
            val originalName = field.name()

            // Skip Airbyte metadata columns - they're already valid
            if (Meta.COLUMN_NAMES.contains(originalName)) {
                return@map field
            }

            val mappedName = inputToFinalColumnNames[originalName] ?: originalName

            if (mappedName != originalName) {
                if (field.isOptional) {
                    Types.NestedField.optional(
                        field.fieldId(),
                        mappedName,
                        field.type(),
                        field.doc(),
                    )
                } else {
                    Types.NestedField.required(
                        field.fieldId(),
                        mappedName,
                        field.type(),
                        field.doc(),
                    )
                }
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
