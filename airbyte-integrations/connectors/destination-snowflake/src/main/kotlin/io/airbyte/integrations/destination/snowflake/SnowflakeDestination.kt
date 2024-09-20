/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.getRawNamespaceOverride
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveDestinationRunner
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.operation.SyncOperation
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.staging.operation.StagingStreamOperations
import io.airbyte.integrations.base.destination.operation.DefaultFlush
import io.airbyte.integrations.base.destination.operation.DefaultSyncOperation
import io.airbyte.integrations.base.destination.typing_deduping.*
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.snowflake.migrations.SnowflakeAbMetaAndGenIdMigration
import io.airbyte.integrations.destination.snowflake.migrations.SnowflakeDV2Migration
import io.airbyte.integrations.destination.snowflake.migrations.SnowflakeState
import io.airbyte.integrations.destination.snowflake.operation.SnowflakeStagingClient
import io.airbyte.integrations.destination.snowflake.operation.SnowflakeStorageOperation
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import io.airbyte.protocol.models.v0.*
import java.util.*
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.function.Consumer
import javax.sql.DataSource
import net.snowflake.client.core.SFSession
import net.snowflake.client.core.SFStatement
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class SnowflakeDestination
@JvmOverloads
constructor(
    private val airbyteEnvironment: String,
    private val nameTransformer: NamingConventionTransformer = SnowflakeSQLNameTransformer(),
) : BaseConnector(), Destination {
    private val destinationColumns = JavaBaseConstants.DestinationColumns.V2_WITH_GENERATION

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        val dataSource = getDataSource(config)
        try {
            val retentionPeriodDays = 1
            val sqlGenerator = SnowflakeSqlGenerator(retentionPeriodDays)
            val database = getDatabase(dataSource)
            val databaseName = config[JdbcUtils.DATABASE_KEY].asText()
            val outputSchema = nameTransformer.getIdentifier(config[JdbcUtils.SCHEMA_KEY].asText())
            val rawTableSchemaName: String =
                if (getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent) {
                    getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get()
                } else {
                    JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                }
            val finalTableName =
                nameTransformer.getIdentifier(
                    "_airbyte_connection_test_" +
                        UUID.randomUUID().toString().replace("-".toRegex(), "")
                )
            val snowflakeDestinationHandler =
                SnowflakeDestinationHandler(databaseName, database, rawTableSchemaName)
            val snowflakeStagingClient = SnowflakeStagingClient(database)
            val snowflakeStorageOperation =
                SnowflakeStorageOperation(
                    sqlGenerator = sqlGenerator,
                    destinationHandler = snowflakeDestinationHandler,
                    retentionPeriodDays,
                    snowflakeStagingClient
                )
            val streamId =
                sqlGenerator.buildStreamId(outputSchema, finalTableName, rawTableSchemaName)
            val streamConfig =
                StreamConfig(
                    id = streamId,
                    postImportAction = ImportType.APPEND,
                    primaryKey = listOf(),
                    cursor = Optional.empty(),
                    columns = linkedMapOf(),
                    generationId = 0,
                    minimumGenerationId = 0,
                    syncId = 0
                )
            // None of the fields in destination initial status matter
            // for a dummy sync with type-dedupe disabled. We only look at these
            // when we perform final table related setup operations.
            // We just need the streamId to perform the calls in streamOperation.
            val initialStatus =
                DestinationInitialStatus(
                    streamConfig = streamConfig,
                    isFinalTablePresent = false,
                    initialRawTableStatus =
                        InitialRawTableStatus(
                            rawTableExists = false,
                            hasUnprocessedRecords = true,
                            maxProcessedTimestamp = Optional.empty()
                        ),
                    initialTempRawTableStatus =
                        InitialRawTableStatus(
                            rawTableExists = false,
                            hasUnprocessedRecords = true,
                            maxProcessedTimestamp = Optional.empty()
                        ),
                    isSchemaMismatch = true,
                    isFinalTableEmpty = true,
                    destinationState =
                        SnowflakeState(needsSoftReset = false, isAirbyteMetaPresentInRaw = false),
                    finalTableGenerationId = null,
                    finalTempTableGenerationId = null,
                )
            // We simulate a mini-sync to see the raw table code path is exercised. and disable T+D
            snowflakeDestinationHandler.createNamespaces(setOf(rawTableSchemaName, outputSchema))

            val streamOperation: StagingStreamOperations<SnowflakeState> =
                StagingStreamOperations(
                    snowflakeStorageOperation,
                    initialStatus,
                    FileUploadFormat.CSV,
                    destinationColumns,
                    disableTypeDedupe = true
                )
            // Dummy message
            val data = """
                {"testKey": "testValue"}
            """.trimIndent()
            val message =
                PartialAirbyteMessage()
                    .withSerialized(data)
                    .withRecord(
                        PartialAirbyteRecordMessage()
                            .withEmittedAt(System.currentTimeMillis())
                            .withMeta(
                                AirbyteRecordMessageMeta(),
                            ),
                    )
            streamOperation.writeRecords(streamConfig, listOf(message).stream())
            streamOperation.finalizeTable(
                streamConfig,
                StreamSyncSummary(1, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE),
            )
            // clean up the raw table, this is intentionally not part of actual sync code
            // because we avoid dropping original tables directly.
            snowflakeDestinationHandler.execute(
                Sql.of(
                    "DROP TABLE IF EXISTS \"${streamId.rawNamespace}\".\"${streamId.rawName}\";",
                ),
            )
            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: Exception) {
            LOGGER.error("Exception while checking connection: ", e)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("Could not connect with provided configuration. ${e.message}")
        } finally {
            try {
                close(dataSource)
            } catch (e: Exception) {
                LOGGER.warn("Unable to close data source.", e)
            }
        }
    }

    private fun getDataSource(config: JsonNode): DataSource {
        return SnowflakeDatabaseUtils.createDataSource(config, airbyteEnvironment)
    }

    private fun getDatabase(dataSource: DataSource): JdbcDatabase {
        return SnowflakeDatabaseUtils.getDatabase(dataSource)
    }

    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {
        AirbyteExceptionHandler.addAllStringsInConfigForDeinterpolation(config)

        val defaultNamespace = config["schema"].asText()
        val retentionPeriodDays =
            getRetentionPeriodDays(
                config[RETENTION_PERIOD_DAYS],
            )
        val useMergeForUpsert =
            config.has(USE_MERGE_FOR_UPSERT) && config[USE_MERGE_FOR_UPSERT].asBoolean(false)
        val sqlGenerator = SnowflakeSqlGenerator(retentionPeriodDays, useMergeForUpsert)
        val database = getDatabase(getDataSource(config))
        val databaseName = config[JdbcUtils.DATABASE_KEY].asText()
        val rawTableSchemaName: String =
            if (getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent) {
                getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get()
            } else {
                JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
            }
        val catalogParser = CatalogParser(sqlGenerator, defaultNamespace, rawTableSchemaName)
        val snowflakeDestinationHandler =
            SnowflakeDestinationHandler(databaseName, database, rawTableSchemaName)
        val parsedCatalog: ParsedCatalog = catalogParser.parseCatalog(catalog)
        val disableTypeDedupe =
            config.has(DISABLE_TYPE_DEDUPE) && config[DISABLE_TYPE_DEDUPE].asBoolean(false)
        val migrations: List<Migration<SnowflakeState>> =
            listOf(
                SnowflakeDV2Migration(
                    nameTransformer,
                    database,
                    databaseName,
                    sqlGenerator,
                ),
                SnowflakeAbMetaAndGenIdMigration(database),
            )

        val snowflakeStagingClient = SnowflakeStagingClient(database)

        val snowflakeStorageOperation =
            SnowflakeStorageOperation(
                sqlGenerator = sqlGenerator,
                destinationHandler = snowflakeDestinationHandler,
                retentionPeriodDays,
                snowflakeStagingClient
            )

        val syncOperation: SyncOperation =
            DefaultSyncOperation(
                parsedCatalog,
                snowflakeDestinationHandler,
                defaultNamespace,
                { initialStatus: DestinationInitialStatus<SnowflakeState>, disableTD ->
                    StagingStreamOperations(
                        snowflakeStorageOperation,
                        initialStatus,
                        FileUploadFormat.CSV,
                        destinationColumns,
                        disableTD
                    )
                },
                migrations,
                disableTypeDedupe
            )

        return AsyncStreamConsumer(
            outputRecordCollector = outputRecordCollector,
            onStart = {},
            onClose = { _, streamSyncSummaries ->
                syncOperation.finalizeStreams(streamSyncSummaries)
                SCHEDULED_EXECUTOR_SERVICE.shutdownNow()
            },
            onFlush = DefaultFlush(optimalFlushBatchSize, syncOperation),
            catalog = catalog,
            bufferManager = BufferManager(defaultNamespace, snowflakeBufferMemoryLimit),
            airbyteMessageDeserializer =
                AirbyteMessageDeserializer(
                    SnowflakeLargeRecordTruncator(parsedCatalog, defaultNamespace)
                )
        )
    }

    private class SnowflakeLargeRecordTruncator(
        private val parsedCatalog: ParsedCatalog,
        private val defaultNamespace: String
    ) : StreamAwareDataTransformer {
        val maxRowSize = 16 * 1_024 * 1_024
        override fun transform(
            streamDescriptor: StreamDescriptor?,
            data: JsonNode?,
            meta: AirbyteRecordMessageMeta?
        ): Pair<JsonNode?, AirbyteRecordMessageMeta?> {
            if (data == null) {
                return Pair(null, meta)
            }
            val metaChanges: MutableList<AirbyteRecordMessageMetaChange> = ArrayList()
            if (meta != null && meta.changes != null) {
                metaChanges.addAll(meta.changes)
            }

            val namespace =
                if (
                    (streamDescriptor!!.namespace != null &&
                        streamDescriptor.namespace.isNotEmpty())
                )
                    streamDescriptor.namespace
                else defaultNamespace
            val streamConfig = parsedCatalog.getStream(namespace, streamDescriptor.name)

            var totalSize = 0
            val finalData = JsonNodeFactory.instance.objectNode()
            val fieldValueByName =
                data.fields().asSequence().associate { it.key to it.value }.toMutableMap()
            for (pkField in streamConfig.primaryKey) {
                val fieldValue = fieldValueByName.remove(pkField.originalName)
                finalData.set<JsonNode>(pkField.originalName, fieldValue)
                totalSize += fieldValue?.toString()?.length ?: 0
            }
            val fieldNameSortedByValueSize =
                fieldValueByName.keys.sortedBy {
                    val fieldLength = fieldValueByName.getValue(it).toString().length
                    fieldLength
                }
            for (fieldName in fieldNameSortedByValueSize) {
                val fieldValue = fieldValueByName.remove(fieldName)
                val fieldSize = fieldValue?.toString()?.length ?: 0
                if (totalSize + fieldSize > maxRowSize) {
                    fieldValueByName[fieldName] = fieldValue
                    break
                }
                finalData.set<JsonNode>(fieldName, fieldValue)
                totalSize += fieldSize
            }
            if (fieldValueByName.isNotEmpty()) {
                LOGGER.info(
                    "removed fields [${fieldValueByName.keys.joinToString(", ")}]. finalSize=$totalSize"
                )
                for (fieldEntry in fieldValueByName) {
                    metaChanges.add(
                        AirbyteRecordMessageMetaChange()
                            .withField(fieldEntry.key)
                            .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                            .withReason(
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_RECORD_SIZE_LIMITATION
                            )
                    )
                }
            }
            return Pair(finalData, AirbyteRecordMessageMeta().withChanges(metaChanges))
        }
    }

    override val isV2Destination: Boolean
        get() = true

    @Throws(Exception::class)
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw UnsupportedOperationException("DV2 destination cannot be called by getConsumer")
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(SnowflakeDestination::class.java)
        const val RAW_SCHEMA_OVERRIDE: String = "raw_data_schema"
        const val RETENTION_PERIOD_DAYS: String = "retention_period_days"
        const val DISABLE_TYPE_DEDUPE: String = "disable_type_dedupe"
        const val USE_MERGE_FOR_UPSERT: String = "use_merge_for_upsert"
        @JvmField
        val SCHEDULED_EXECUTOR_SERVICE: ScheduledExecutorService =
            Executors.newScheduledThreadPool(1)

        fun getRetentionPeriodDays(node: JsonNode?): Int {
            val retentionPeriodDays =
                if (node == null || node.isNull) {
                    1
                } else {
                    node.asInt()
                }
            return retentionPeriodDays
        }

        private val snowflakeBufferMemoryLimit: Long
            get() = (Runtime.getRuntime().maxMemory() * 0.5).toLong()

        // The per stream size limit is following recommendations from:
        // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
        // "To optimize the number of parallel operations for a load,
        // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size
        // compressed."
        private val optimalFlushBatchSize: Long
            get() = (200 * 1024 * 1024).toLong()
    }
}

fun main(args: Array<String>) {
    IntegrationRunner.addOrphanedThreadFilter { threadInfo: IntegrationRunner.OrphanedThreadInfo ->
        for (stackTraceElement in threadInfo.threadCreationInfo.stack) {
            val stackClassName = stackTraceElement.className
            val stackMethodName = stackTraceElement.methodName
            if (
                SFStatement::class.java.canonicalName == stackClassName &&
                    "close" == stackMethodName ||
                    SFSession::class.java.canonicalName == stackClassName &&
                        "callHeartBeatWithQueryTimeout" == stackMethodName
            ) {
                return@addOrphanedThreadFilter false
            }
        }
        true
    }
    AirbyteExceptionHandler.addThrowableForDeinterpolation(
        SnowflakeSQLException::class.java,
    )
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination {
            SnowflakeDestination(
                OssCloudEnvVarConsts.AIRBYTE_OSS,
            )
        }
        .withCloudDestination {
            SnowflakeDestination(
                OssCloudEnvVarConsts.AIRBYTE_CLOUD,
            )
        }
        .run(args)
}
