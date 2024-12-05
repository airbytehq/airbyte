/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.factory.DataSourceFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility.emitConfigErrorTrace
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.getRawNamespaceOverride
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination.Companion.DISABLE_TYPE_DEDUPE
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination.Companion.RAW_SCHEMA_OVERRIDE
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryption
import io.airbyte.cdk.integrations.destination.s3.EncryptionConfig
import io.airbyte.cdk.integrations.destination.s3.EncryptionConfig.Companion.fromJson
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.NoEncryption
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.attemptS3WriteAndDelete
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.staging.operation.StagingStreamOperations
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.integrations.base.destination.operation.DefaultFlush
import io.airbyte.integrations.base.destination.operation.DefaultSyncOperation
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants
import io.airbyte.integrations.destination.redshift.operation.RedshiftStagingStorageOperation
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDV2Migration
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftGenerationIdMigration
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftRawTableAirbyteMetaMigration
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftState
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSuperLimitationTransformer
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.sql.SQLException
import java.time.Duration
import java.util.Objects
import java.util.Optional
import java.util.UUID
import java.util.concurrent.Executors
import java.util.function.Consumer
import javax.sql.DataSource
import org.apache.commons.lang3.NotImplementedException
import org.jetbrains.annotations.VisibleForTesting
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class RedshiftDestination : BaseConnector(), Destination {
    private fun isEphemeralKeysAndPurgingStagingData(
        config: JsonNode,
        encryptionConfig: EncryptionConfig
    ): Boolean {
        return !isPurgeStagingData(config) &&
            encryptionConfig is AesCbcEnvelopeEncryption &&
            encryptionConfig.keyType == AesCbcEnvelopeEncryption.KeyType.EPHEMERAL
    }

    @Throws(Exception::class)
    override fun spec(): ConnectorSpecification {
        // inject the standard ssh configuration into the spec.
        val originalSpec = super.spec()
        val propNode = originalSpec.connectionSpecification["properties"] as ObjectNode
        propNode.set<JsonNode>("tunnel_method", deserialize(readResource("ssh-tunnel-spec.json")))
        return originalSpec
    }

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        val s3Config: S3DestinationConfig =
            S3DestinationConfig.getS3DestinationConfig(RedshiftUtil.findS3Options(config))
        val encryptionConfig =
            if (config.has(RedshiftDestinationConstants.UPLOADING_METHOD))
                fromJson(
                    config[RedshiftDestinationConstants.UPLOADING_METHOD][JdbcUtils.ENCRYPTION_KEY]
                )
            else NoEncryption()
        if (isEphemeralKeysAndPurgingStagingData(config, encryptionConfig)) {
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    "You cannot use ephemeral keys and disable purging your staging data. This would produce S3 objects that you cannot decrypt."
                )
        }
        attemptS3WriteAndDelete(getS3StorageOperations(s3Config), s3Config, s3Config.bucketPath)

        val dataSource = getDataSource(config)
        try {
            val database: JdbcDatabase = DefaultJdbcDatabase(dataSource)
            val outputSchema = namingResolver.getIdentifier(config[JdbcUtils.SCHEMA_KEY].asText())
            val rawTableSchemaName: String =
                if (getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent) {
                    getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get()
                } else {
                    JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                }
            val finalTableName =
                namingResolver.getIdentifier(
                    "_airbyte_connection_test_" +
                        UUID.randomUUID().toString().replace("-".toRegex(), "")
                )

            val sqlGenerator = getSqlGenerator(config)
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

            val databaseName = getDatabaseName(config)
            val destinationHandler =
                RedshiftDestinationHandler(databaseName, database, rawTableSchemaName)
            val storageOperation =
                RedshiftStagingStorageOperation(
                    s3Config,
                    keepStagingFiles = false,
                    getS3StorageOperations(s3Config),
                    sqlGenerator,
                    destinationHandler,
                    RedshiftSqlGenerator.isDropCascade(config),
                )

            // We simulate a mini-sync to see the raw table code path is exercised. and disable T+D
            destinationHandler.createNamespaces(setOf(rawTableSchemaName, outputSchema))
            val streamOperation: StagingStreamOperations<RedshiftState> =
                StagingStreamOperations(
                    storageOperation,
                    // None of the fields in destination initial status matter
                    // for a dummy sync with type-dedupe disabled. We only look at these
                    // when we perform final table related setup operations.
                    // We just need the streamId to perform the calls in streamOperation.
                    DestinationInitialStatus(
                        streamConfig = streamConfig,
                        isFinalTablePresent = false,
                        initialRawTableStatus =
                            InitialRawTableStatus(
                                rawTableExists = false,
                                hasUnprocessedRecords = true,
                                maxProcessedTimestamp = Optional.empty(),
                            ),
                        initialTempRawTableStatus =
                            InitialRawTableStatus(
                                rawTableExists = false,
                                hasUnprocessedRecords = true,
                                maxProcessedTimestamp = Optional.empty(),
                            ),
                        isSchemaMismatch = true,
                        isFinalTableEmpty = true,
                        destinationState =
                            RedshiftState(
                                needsSoftReset = false,
                                isAirbyteMetaPresentInRaw = true,
                                isGenerationIdPresent = true,
                            ),
                        finalTableGenerationId = 1,
                        finalTempTableGenerationId = 1,
                    ),
                    FileUploadFormat.CSV,
                    destinationColumns,
                    disableTypeDedupe = true,
                )
            streamOperation.writeRecords(
                streamConfig,
                listOf(
                        // Dummy message
                        PartialAirbyteMessage()
                            .withSerialized("""{"testKey": "testValue"}""")
                            .withRecord(
                                PartialAirbyteRecordMessage()
                                    .withEmittedAt(System.currentTimeMillis())
                                    .withMeta(
                                        AirbyteRecordMessageMeta(),
                                    ),
                            )
                    )
                    .stream()
            )
            streamOperation.finalizeTable(
                streamConfig,
                StreamSyncSummary(recordsWritten = 1, AirbyteStreamStatus.COMPLETE),
            )

            // And now that we have a table, simulate the next sync startup.
            destinationHandler.gatherInitialState(listOf(streamConfig))
            // (not bothering to verify the return value, maybe we should?)

            // clean up the raw table, this is intentionally not part of actual sync code
            // because we avoid dropping original tables directly.
            destinationHandler.execute(
                Sql.of(
                    "DROP TABLE IF EXISTS \"${streamId.rawNamespace}\".\"${streamId.rawName}\";",
                ),
            )

            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: SQLException) {
            // copied from AbstractJdbcDestination's attemptTableOperations
            val stateCode: String = e.sqlState
            val errorCode: Int
            val exceptionMessage: String?
            if (Objects.isNull(e.cause) || e.cause !is SQLException) {
                errorCode = e.errorCode
                exceptionMessage = e.message
            } else {
                val cause = e.cause as SQLException
                errorCode = cause.errorCode
                exceptionMessage = cause.message
            }
            val message = getErrorMessage(stateCode, errorCode, exceptionMessage, e)
            emitConfigErrorTrace(e, message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(message)
        } catch (e: Exception) {
            LOGGER.error("Exception while checking connection: ", e)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    """
                    Could not connect with provided configuration. 
                    ${e.message}
                    """.trimIndent()
                )
        } finally {
            try {
                close(dataSource)
            } catch (e: Exception) {
                LOGGER.warn("Unable to close data source.", e)
            }
        }
    }

    override val isV2Destination: Boolean = true

    @VisibleForTesting
    fun getDataSource(config: JsonNode): DataSource {
        val jdbcConfig: JsonNode = getJdbcConfig(config)
        return create(
            jdbcConfig[JdbcUtils.USERNAME_KEY].asText(),
            if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY)) jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
            else null,
            DRIVER_CLASS,
            jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
            getDefaultConnectionProperties(),
            Duration.ofMinutes(2)
        )
    }

    @VisibleForTesting
    fun getDatabase(dataSource: DataSource): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource)
    }

    fun getDatabase(dataSource: DataSource, sourceOperations: JdbcSourceOperations?): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource, sourceOperations)
    }

    private val namingResolver: NamingConventionTransformer
        get() = RedshiftSQLNameTransformer()

    private fun getDefaultConnectionProperties(): Map<String, String> {
        // The following properties can be overriden through jdbcUrlParameters in the config.
        val connectionOptions: MutableMap<String, String> = HashMap()
        // Redshift properties
        // https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-configuration-options.html#jdbc20-connecttimeout-option
        // connectTimeout is different from Hikari pool's connectionTimout, driver defaults to
        // 10seconds so
        // increase it to match hikari's default
        connectionOptions["connectTimeout"] = "120"
        // HikariPool properties
        // https://github.com/brettwooldridge/HikariCP?tab=readme-ov-file#frequently-used
        // connectionTimeout is set explicitly to 2 minutes when creating data source.
        // Do aggressive keepAlive with minimum allowed value, this only applies to connection
        // sitting idle
        // in the pool.
        connectionOptions["keepaliveTime"] = Duration.ofSeconds(30).toMillis().toString()
        connectionOptions.putAll(SSL_JDBC_PARAMETERS)
        return connectionOptions
    }

    private fun getSqlGenerator(config: JsonNode): RedshiftSqlGenerator {
        return RedshiftSqlGenerator(namingResolver, config)
    }

    private fun getMigrations(
        database: JdbcDatabase,
        databaseName: String,
        sqlGenerator: RedshiftSqlGenerator
    ): List<Migration<RedshiftState>> {
        return listOf(
            RedshiftDV2Migration(
                namingResolver,
                database,
                databaseName,
                sqlGenerator,
            ),
            RedshiftRawTableAirbyteMetaMigration(database, databaseName),
            RedshiftGenerationIdMigration(database, databaseName)
        )
    }

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    private fun getDataTransformer(
        parsedCatalog: ParsedCatalog?,
        defaultNamespace: String?
    ): StreamAwareDataTransformer {
        // Redundant override to keep in consistent with InsertDestination. TODO: Unify these 2
        // classes with
        // composition.
        return RedshiftSuperLimitationTransformer(parsedCatalog, defaultNamespace!!)
    }

    @Deprecated("")
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw NotImplementedException("Should use the getSerializedMessageConsumer instead")
    }

    @Throws(Exception::class)
    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {
        if (config.has(RedshiftDestinationConstants.UPLOADING_METHOD))
            fromJson(
                config[RedshiftDestinationConstants.UPLOADING_METHOD][JdbcUtils.ENCRYPTION_KEY]
            )
        else NoEncryption()
        val s3Options = RedshiftUtil.findS3Options(config)
        val s3Config: S3DestinationConfig = S3DestinationConfig.getS3DestinationConfig(s3Options)
        val defaultNamespace = config["schema"].asText()

        val sqlGenerator = RedshiftSqlGenerator(namingResolver, config)
        val parsedCatalog: ParsedCatalog
        val database = getDatabase(getDataSource(config))
        val databaseName = config[JdbcUtils.DATABASE_KEY].asText()
        val catalogParser: CatalogParser
        val rawNamespace: String
        if (getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent) {
            rawNamespace = getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get()
            catalogParser = CatalogParser(sqlGenerator, defaultNamespace, rawNamespace)
        } else {
            rawNamespace = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
            catalogParser = CatalogParser(sqlGenerator, defaultNamespace, rawNamespace)
        }
        val redshiftDestinationHandler =
            RedshiftDestinationHandler(databaseName, database, rawNamespace)
        parsedCatalog = catalogParser.parseCatalog(catalog)
        val disableTypeDedupe =
            config.has(DISABLE_TYPE_DEDUPE) && config[DISABLE_TYPE_DEDUPE].asBoolean(false)
        val redshiftMigrations: List<Migration<RedshiftState>> =
            getMigrations(database, databaseName, sqlGenerator)

        val s3StorageOperations = getS3StorageOperations(s3Config)

        val redshiftStagingStorageOperation =
            RedshiftStagingStorageOperation(
                s3Config,
                isPurgeStagingData(s3Options),
                s3StorageOperations,
                sqlGenerator,
                redshiftDestinationHandler,
                RedshiftSqlGenerator.isDropCascade(config),
            )
        val syncOperation =
            DefaultSyncOperation(
                parsedCatalog,
                redshiftDestinationHandler,
                defaultNamespace,
                { initialStatus, disableTD ->
                    StagingStreamOperations(
                        redshiftStagingStorageOperation,
                        initialStatus,
                        FileUploadFormat.CSV,
                        destinationColumns,
                        disableTD
                    )
                },
                redshiftMigrations,
                disableTypeDedupe,
            )
        return AsyncStreamConsumer(
            outputRecordCollector,
            onStart = {},
            onClose = { _, streamSyncSummaries ->
                syncOperation.finalizeStreams(streamSyncSummaries)
            },
            onFlush = DefaultFlush(OPTIMAL_FLUSH_BATCH_SIZE, syncOperation),
            catalog,
            BufferManager(defaultNamespace, bufferMemoryLimit),
            FlushFailure(),
            Executors.newFixedThreadPool(5),
            AirbyteMessageDeserializer(getDataTransformer(parsedCatalog, defaultNamespace)),
        )
    }

    private fun getS3StorageOperations(s3Config: S3DestinationConfig) =
        S3StorageOperations(namingResolver, s3Config.getS3Client(), s3Config)

    private fun isPurgeStagingData(config: JsonNode?): Boolean {
        return !config!!.has("purge_staging_data") || config["purge_staging_data"].asBoolean()
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(RedshiftDestination::class.java)

        val DRIVER_CLASS: String = DatabaseDriver.REDSHIFT.driverClassName
        val SSL_JDBC_PARAMETERS: Map<String, String> =
            ImmutableMap.of(
                JdbcUtils.SSL_KEY,
                "true",
                "sslfactory",
                "com.amazon.redshift.ssl.NonValidatingFactory"
            )

        private val destinationColumns = JavaBaseConstants.DestinationColumns.V2_WITH_GENERATION

        private const val OPTIMAL_FLUSH_BATCH_SIZE: Long = 50 * 1024 * 1024
        private val bufferMemoryLimit: Long = (Runtime.getRuntime().maxMemory() * 0.5).toLong()

        private fun getDatabaseName(config: JsonNode): String {
            return config[JdbcUtils.DATABASE_KEY].asText()
        }

        private fun sshWrappedDestination(): Destination {
            return SshWrappedDestination(
                RedshiftDestination(),
                JdbcUtils.HOST_LIST_KEY,
                JdbcUtils.PORT_LIST_KEY
            )
        }

        fun getJdbcConfig(redshiftConfig: JsonNode): JsonNode {
            val schema =
                Optional.ofNullable(redshiftConfig[JdbcUtils.SCHEMA_KEY])
                    .map { obj: JsonNode -> obj.asText() }
                    .orElse("public")
            val configBuilder =
                ImmutableMap.builder<Any, Any>()
                    .put(JdbcUtils.USERNAME_KEY, redshiftConfig[JdbcUtils.USERNAME_KEY].asText())
                    .put(JdbcUtils.PASSWORD_KEY, redshiftConfig[JdbcUtils.PASSWORD_KEY].asText())
                    .put(
                        JdbcUtils.JDBC_URL_KEY,
                        String.format(
                            "jdbc:redshift://%s:%s/%s",
                            redshiftConfig[JdbcUtils.HOST_KEY].asText(),
                            redshiftConfig[JdbcUtils.PORT_KEY].asText(),
                            redshiftConfig[JdbcUtils.DATABASE_KEY].asText()
                        )
                    )
                    .put(JdbcUtils.SCHEMA_KEY, schema)

            if (redshiftConfig.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
                configBuilder.put(
                    JdbcUtils.JDBC_URL_PARAMS_KEY,
                    redshiftConfig[JdbcUtils.JDBC_URL_PARAMS_KEY]
                )
            }

            return jsonNode(configBuilder.build())
        }

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            val destination: Destination = sshWrappedDestination()
            LOGGER.info("starting destination: {}", RedshiftDestination::class.java)
            IntegrationRunner(destination).run(args)
            LOGGER.info("completed destination: {}", RedshiftDestination::class.java)
        }
    }
}
