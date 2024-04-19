package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeTransaction
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean

private val log = KotlinLogging.logger {}
class DatabricksSqlOperations (
    private val sqlGenerator: SqlGenerator,
    private val destinationHandler: DestinationHandler<MinimumDestinationState>
) : SqlOperations<MinimumDestinationState> {

    private val overwriteFinalTableWithTmp: AtomicBoolean = AtomicBoolean(false)
    override fun prepare(destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState>): Result<Unit> {
        return kotlin.runCatching {
            val streamConfig = destinationInitialStatus.streamConfig
            prepareStagingTable(streamConfig.id, streamConfig.destinationSyncMode!!)
            prepareFinalTable(destinationInitialStatus)
        }
    }

    private fun prepareStagingTable(streamId: StreamId, destinationSyncMode: DestinationSyncMode) {
        val rawSchema = streamId.rawNamespace
        // TODO: Optimize by running SHOW SCHEMAS; rather than CREATE SCHEMA if not exists
        destinationHandler.execute(sqlGenerator.createSchema(rawSchema))

        // TODO: Optimize by running SHOW TABLES; truncate or create based on mode
        // Create raw tables.
        val createRawTableSql = Sql.of("""
                CREATE TABLE IF NOT EXISTS ${streamId.rawNamespace}.${streamId.rawName} (
                    ${JavaBaseConstants.COLUMN_NAME_AB_RAW_ID} STRING,
                    ${JavaBaseConstants.COLUMN_NAME_DATA} STRING,
                    ${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT} TIMESTAMP,
                    ${JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT} TIMESTAMP,
                    ${JavaBaseConstants.COLUMN_NAME_AB_META} STRING
                )
            """.trimIndent())
        destinationHandler.execute(createRawTableSql)
        // Truncate the raw table if sync in OVERWRITE.
        if (destinationSyncMode == DestinationSyncMode.OVERWRITE) {
            val truncateTableSql = Sql.of("TRUNCATE TABLE ${streamId.rawNamespace}.${streamId.rawName}")
            destinationHandler.execute(truncateTableSql)
        }
    }

    private fun prepareFinalTableForOverwrite(initialStatus: DestinationInitialStatus<MinimumDestinationState>) {
        val stream = initialStatus.streamConfig
        if (!initialStatus.isFinalTableEmpty || initialStatus.isSchemaMismatch) {
            // We want to overwrite an existing table. Write into a tmp table.
            // We'll overwrite the table at the
            // end of the sync.
            overwriteFinalTableWithTmp.set(true)
            // overwrite an existing tmp table if needed.
            destinationHandler.execute(
                sqlGenerator.createTable(
                    stream,
                    TMP_OVERWRITE_TABLE_SUFFIX,
                    true
                )
            )
            log.info {
                "Using temp final table for stream ${stream.id.finalName}, will overwrite existing table at end of sync"
            }
        } else {
            log.info {
                "Final Table for stream ${stream.id.finalName} is empty and matches the expected v2 format, writing to table directly"
            }
        }
    }

    private fun prepareFinalTable(initialStatus: DestinationInitialStatus<MinimumDestinationState>) {
        val stream = initialStatus.streamConfig
        // No special handling if final table doesn't exist, just create and return
        if (!initialStatus.isFinalTablePresent) {
            log.info {
                "Final table does not exist for stream ${initialStatus.streamConfig.id.finalName}, creating."
            }
            val finalSchema = stream.id.finalNamespace
            // TODO: Optimize by running SHOW SCHEMAS; rather than CREATE SCHEMA if not exists
            destinationHandler.execute(sqlGenerator.createSchema(finalSchema))
            // The table doesn't exist. Create it. Don't force.
            destinationHandler.execute(
                sqlGenerator.createTable(stream, NO_SUFFIX, false)
            )
            return
        }

        log.info {
            "Final Table exists for stream ${stream.id.finalName}"
        }
        // The table already exists. Decide whether we're writing to it directly, or
        // using a tmp table.
        when (stream.destinationSyncMode!!) {
            DestinationSyncMode.OVERWRITE -> prepareFinalTableForOverwrite(initialStatus)
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP -> {
                if (initialStatus.isSchemaMismatch || initialStatus.destinationState.needsSoftReset()) {
                    // We're loading data directly into the existing table.
                    // Make sure it has the right schema.
                    // Also, if a raw table migration wants us to do a soft reset, do that
                    // here.
                    TypeAndDedupeTransaction.executeSoftReset(
                        sqlGenerator,
                        destinationHandler,
                        stream
                    )
                }
            }
        }
    }


    override fun copyIntoTableFromStage(stageId: String, streamId: StreamId): Result<Unit> {
        TODO("Not yet implemented")
    }

    override fun updateFinalTable(streamConfig: StreamConfig): Result<Unit> {
        TODO("Not yet implemented")
    }

    companion object {
        private const val NO_SUFFIX = ""
        private const val TMP_OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp"
    }
}
