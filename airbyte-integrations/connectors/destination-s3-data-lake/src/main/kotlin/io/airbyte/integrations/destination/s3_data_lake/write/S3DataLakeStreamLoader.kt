/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.write

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
import io.airbyte.integrations.destination.s3_data_lake.catalog.S3DataLakeUtil
import io.airbyte.integrations.destination.s3_data_lake.schema.S3DataLakeTableSchemaMapper
import io.airbyte.integrations.destination.s3_data_lake.spec.AllowNonReversibleUpgrades
import io.airbyte.integrations.destination.s3_data_lake.spec.DEFAULT_CATALOG_NAME
import io.airbyte.integrations.destination.s3_data_lake.spec.IcebergDeleteFileType
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.types.Types

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3DataLakeStreamLoader(
    private val icebergConfiguration: S3DataLakeConfiguration,
    override val stream: DestinationStream,
    private val icebergTableSynchronizer: IcebergTableSynchronizer,
    private val s3DataLakeUtil: S3DataLakeUtil,
    private val icebergUtil: IcebergUtil,
    private val tableIdGenerator: TableIdGenerator,
    private val stagingBranchName: String,
    private val mainBranchName: String,
    private val streamStateStore: StreamStateStore<S3DataLakeStreamState>,
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
    private val incomingSchema: Schema =
        withFinalColumnNames(icebergUtil.toIcebergSchema(stream = stream))

    /**
     * Renames top-level columns from input names to final names (resolved by the CDK's
     * [io.airbyte.cdk.load.schema.TableSchemaMapper]), keeping field IDs intact.
     */
    private fun withFinalColumnNames(schema: Schema): Schema {
        val fields =
            schema.columns().map { field ->
                val inputName = field.name()
                val finalName =
                    if (inputName in Meta.COLUMN_NAMES) inputName
                    else stream.tableSchema.getFinalColumnName(inputName)
                if (finalName == inputName) field
                else Types.NestedField.from(field).withName(finalName).build()
            }
        return Schema(fields, schema.identifierFieldIds())
    }

    /**
     * Refuses to sync when enabling `normalize_column_names` would rename existing columns (which
     * would appear as drop + add, silently discarding data). Truncate refreshes are allowed since
     * they rebuild the table.
     */
    private fun failOnNormalizationRenames(existingSchema: Schema) {
        if (!icebergConfiguration.normalizeColumnNames || stream.isSingleGenerationTruncate()) {
            return
        }
        val incomingNames = incomingSchema.columns().map { it.name() }.toSet()
        val renames =
            existingSchema
                .columns()
                .map { it.name() }
                .filter { it !in incomingNames }
                .mapNotNull { existing ->
                    val normalized = S3DataLakeTableSchemaMapper.normalizeColumnName(existing)
                    if (normalized in incomingNames) "$existing -> $normalized" else null
                }
        if (renames.isNotEmpty()) {
            throw ConfigErrorException(
                "Table ${stream.mappedDescriptor.toPrettyString()} has columns whose normalized " +
                    "names match columns in the incoming schema: ${renames.joinToString(", ")}. " +
                    "This usually means the 'Normalize Column Names' option was changed after the " +
                    "table was created. Clear this stream's data and run a full refresh so the " +
                    "table is recreated with the new column names."
            )
        }
    }

    @SuppressFBWarnings(
        "RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE",
        "something about the `table` lateinit var is confusing spotbugs"
    )
    override suspend fun start() {
        val properties = s3DataLakeUtil.toCatalogProperties(config = icebergConfiguration)
        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, properties)
        s3DataLakeUtil.createNamespaceWithGlueHandling(stream.mappedDescriptor, catalog)
        val targetFormatVersion = icebergConfiguration.tableFormatVersion.formatVersion
        val tableExisted =
            catalog.tableExists(tableIdGenerator.toTableIdentifier(stream.mappedDescriptor))
        table =
            icebergUtil.createTable(
                streamDescriptor = stream.mappedDescriptor,
                catalog = catalog,
                schema = incomingSchema,
                formatVersion = targetFormatVersion,
            )
        val effectiveFormatVersion =
            reconcileFormatVersion(
                table = table,
                tableExisted = tableExisted,
                targetFormatVersion = targetFormatVersion,
                catalog = catalog,
            )
        val deleteMode = resolveDeleteMode(table, effectiveFormatVersion)
        failOnNormalizationRenames(table.schema())

        // Note that if we have columnTypeChangeBehavior OVERWRITE, we don't commit the schema
        // change immediately. This is intentional.
        // If we commit the schema change right now, then affected columns might become unqueryable.
        // Instead, we write data using the new schema to the staging branch - that data will be
        // un-queryable during the sync (which is fine).
        // Also note that we're not wrapping the entire sync in a transaction
        // (i.e. `table.newTransaction()`).
        // This is also intentional - the airbyte protocol requires that we commit data
        // incrementally, and if the entire sync is in a transaction, we might crash before we can
        // commit that transaction.
        targetSchema = computeOrExecuteSchemaUpdate().schema
        logger.info {
            "Creating staging branch $stagingBranchName for stream ${stream.mappedDescriptor}"
        }
        try {
            table.manageSnapshots().createBranch(stagingBranchName).commit()
        } catch (_: IllegalArgumentException) {
            logger.info {
                "Staging branch $stagingBranchName already exists for stream ${stream.mappedDescriptor}; reusing it for recovery."
            }
        }
        stagingBranchCreated = true

        val resolvedDeletesEnabled =
            stream.tableSchema.importType is Dedupe && deleteMode != IcebergDeleteMode.EQUALITY
        val identifierFieldIds =
            if (resolvedDeletesEnabled) {
                targetSchema.identifierFieldIds()
            } else {
                emptySet()
            }
        val optimizePriorIcebergDeleteFiles = icebergConfiguration.optimizePriorIcebergDeleteFiles
        val positionalDeleteState =
            if (resolvedDeletesEnabled) {
                enableIdentifierBloomFilters(table, targetSchema, identifierFieldIds)
                PositionalDeleteResolutionState()
            } else {
                null
            }

        val state =
            S3DataLakeStreamState(
                table = table,
                schema = targetSchema,
                stagingBranchName = stagingBranchName,
                positionalDeleteState = positionalDeleteState,
                optimizePriorIcebergDeleteFiles = optimizePriorIcebergDeleteFiles,
                deleteMode = deleteMode,
            )
        streamStateStore.put(stream.mappedDescriptor, state)
    }

    /**
     * Reconciles the table's actual format version with the configured target, upgrading an
     * existing v2 table to v3 in place when the configuration allows it. Applies to every stream
     * regardless of import type. Returns the table's effective format version.
     */
    private fun reconcileFormatVersion(
        table: Table,
        tableExisted: Boolean,
        targetFormatVersion: Int,
        catalog: org.apache.iceberg.catalog.Catalog,
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
                            branch = mainBranchName,
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

    /** Resolves the delete-file encoding for this stream from the table's format version. */
    private fun resolveDeleteMode(table: Table, effectiveVersion: Int): IcebergDeleteMode {
        if (stream.tableSchema.importType !is Dedupe) {
            return IcebergDeleteMode.EQUALITY
        }
        return when (icebergConfiguration.icebergDeleteFileType) {
            IcebergDeleteFileType.AUTOMATIC ->
                if (effectiveVersion >= 3) IcebergDeleteMode.DELETION_VECTOR
                else IcebergDeleteMode.EQUALITY
            IcebergDeleteFileType.EQUALITY -> IcebergDeleteMode.EQUALITY
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
                "Stream ${stream.mappedDescriptor} did not complete successfully. Keeping staging branch $stagingBranchName for recovery."
            }
            return
        }

        // Doing it first to make sure that data coming in the current batch is written to
        // the main branch
        logger.info {
            "No stream failure detected. Committing changes from staging branch '$stagingBranchName' to main branch '$mainBranchName'."
        }
        // We've modified the table over the sync (i.e. adding new snapshots)
        // so we need to refresh here to get the latest table metadata.
        // In principle, this doesn't matter, but the iceberg SDK throws an error about
        // stale table metadata without this.
        table.refresh()
        // Commit all pending schema updates in order (important for two-phase commits)
        computeOrExecuteSchemaUpdate().pendingUpdates.forEach { it.commit() }
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
    }

    @SuppressFBWarnings(
        "RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE",
        justification = "Kotlin lateinit table access confuses spotbugs"
    )
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
